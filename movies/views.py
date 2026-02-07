from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages

from .models import Movie, Theater, Seat, Booking, SeatReservation, GENRE_CHOICES, LANGUAGE_CHOICES
from .utils import send_booking_confirmation_email

# Seat reservation timeout in minutes
RESERVATION_TIMEOUT_MINUTES = 5


def _release_expired_reservations():
    """Release seats that have exceeded reservation timeout."""
    expired = SeatReservation.objects.filter(expires_at__lt=timezone.now())
    for res in expired:
        res.seat.is_booked = False
        res.seat.save()
    expired.delete()


def movie_list(request):
    """Movie list with genre and language filters."""
    _release_expired_reservations()

    movies = Movie.objects.all()
    search_query = request.GET.get('search')
    genre_filter = request.GET.get('genre')
    language_filter = request.GET.get('language')

    if search_query:
        movies = movies.filter(name__icontains=search_query)
    if genre_filter:
        movies = movies.filter(genre=genre_filter)
    if language_filter:
        movies = movies.filter(language=language_filter)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': GENRE_CHOICES,
        'languages': LANGUAGE_CHOICES,
        'selected_genre': genre_filter,
        'selected_language': language_filter,
    })


def movie_detail(request, movie_id):
    """Movie detail page with YouTube trailer embed."""
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    embed_url = movie.get_youtube_embed_url()
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'theaters': theaters,
        'embed_url': embed_url,
    })


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})


@login_required(login_url='/login/')
def reserve_seats(request, theater_id):
    """Reserve seats temporarily (5 min). Returns to payment page."""
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    _release_expired_reservations()

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        if not selected_seats:
            return render(request, 'movies/seat_selection.html', {
                'theaters': theater,
                'seats': seats,
                'error': 'Please select at least one seat.',
            })

        expires_at = timezone.now() + timezone.timedelta(minutes=RESERVATION_TIMEOUT_MINUTES)
        error_seats = []

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            SeatReservation.objects.update_or_create(
                seat=seat,
                theater=theater,
                defaults={'user': request.user, 'expires_at': expires_at}
            )
            seat.is_booked = True
            seat.save()

        if error_seats:
            return render(request, 'movies/seat_selection.html', {
                'theaters': theater,
                'seats': seats,
                'error': f'Seats {", ".join(error_seats)} are already booked.',
            })

        # Redirect to payment
        seat_ids = request.POST.getlist('seats')
        request.session['pending_booking'] = {
            'theater_id': theater_id,
            'seat_ids': [int(s) for s in seat_ids],
            'reserved_at': timezone.now().isoformat(),
        }
        return redirect('payment_page', theater_id=theater_id)

    return render(request, 'movies/seat_selection.html', {'theaters': theater, 'seats': seats})


@login_required(login_url='/login/')
def payment_page(request, theater_id):
    """Payment page with Razorpay integration."""
    theater = get_object_or_404(Theater, id=theater_id)
    pending = request.session.get('pending_booking', {})

    if pending.get('theater_id') != theater_id:
        messages.error(request, 'Session expired. Please select seats again.')
        return redirect('theater_list', movie_id=theater.movie.id)

    seat_ids = pending.get('seat_ids', [])
    seats = Seat.objects.filter(id__in=seat_ids, theater=theater)

    # Verify seats are still reserved
    for seat in seats:
        res = SeatReservation.objects.filter(seat=seat, theater=theater, user=request.user).first()
        if not res or res.expires_at < timezone.now():
            _release_expired_reservations()
            messages.error(request, 'Your reservation has expired. Please select seats again.')
            return redirect('theater_list', movie_id=theater.movie.id)

    ticket_price = theater.movie.ticket_price
    total_amount = float(ticket_price) * len(seats)

    return render(request, 'movies/payment.html', {
        'theater': theater,
        'seats': seats,
        'total_amount': total_amount,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    })


@login_required(login_url='/login/')
def payment_success(request):
    """Handle successful payment - create booking, send email."""
    if request.method != 'POST':
        return redirect('profile')

    theater_id = request.POST.get('theater_id')
    seat_ids = request.POST.getlist('seat_ids')
    payment_id = request.POST.get('payment_id', '')
    amount = request.POST.get('amount', 0)

    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(id__in=seat_ids, theater=theater)

    # Clean up reservations and create bookings
    ticket_price = theater.movie.ticket_price or 0
    seat_numbers = []
    for seat in seats:
        SeatReservation.objects.filter(seat=seat, theater=theater).delete()
        Booking.objects.create(
            user=request.user,
            seat=seat,
            movie=theater.movie,
            theater=theater,
            amount=ticket_price,
            payment_status='completed',
            payment_id=payment_id,
        )
        seat.is_booked = True
        seat.save()
        seat_numbers.append(seat.seat_number)

    # Clear session
    if 'pending_booking' in request.session:
        del request.session['pending_booking']

    # Send email confirmation
    if request.user.email:
        send_booking_confirmation_email(
            user=request.user,
            movie_name=theater.movie.name,
            theater_name=theater.name,
            show_time=theater.time.strftime('%d %b %Y, %I:%M %p'),
            seats=', '.join(seat_numbers),
            amount=amount,
            booking_id=payment_id or f'BMS-{timezone.now().strftime("%Y%m%d%H%M")}',
        )

    messages.success(request, 'Booking confirmed! Check your email for details.')
    return redirect('profile')


@login_required(login_url='/login/')
def payment_failed(request):
    """Handle failed payment - release reserved seats."""
    theater_id = request.GET.get('theater_id') or request.POST.get('theater_id')
    if theater_id:
        pending = request.session.get('pending_booking', {})
        if pending.get('theater_id') == int(theater_id):
            theater = Theater.objects.filter(id=theater_id).first()
            if theater:
                for seat_id in pending.get('seat_ids', []):
                    seat = Seat.objects.filter(id=seat_id, theater=theater).first()
                    if seat:
                        SeatReservation.objects.filter(seat=seat, theater=theater).delete()
                        seat.is_booked = False
                        seat.save()
            if 'pending_booking' in request.session:
                del request.session['pending_booking']

    messages.error(request, 'Payment failed. Your seats have been released.')
    return redirect('profile')


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    """Legacy direct booking (no payment) - for backwards compatibility.
    New flow: reserve_seats -> payment -> payment_success.
    """
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        error_seats = []

        if not selected_seats:
            return render(request, 'movies/seat_selection.html', {
                'theaters': theater,
                'seats': seats,
                'error': 'No seat selected.',
            })

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                ticket_price = theater.movie.ticket_price or 0
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theater.movie,
                    theater=theater,
                    amount=ticket_price,
                    payment_status='completed',
                )
                seat.is_booked = True
                seat.save()

                # Send email
                if request.user.email:
                    send_booking_confirmation_email(
                        user=request.user,
                        movie_name=theater.movie.name,
                        theater_name=theater.name,
                        show_time=theater.time.strftime('%d %b %Y, %I:%M %p'),
                        seats=seat.seat_number,
                        amount=str(ticket_price),
                        booking_id=f'BMS-{timezone.now().strftime("%Y%m%d%H%M")}',
                    )
            except IntegrityError:
                error_seats.append(seat.seat_number)

        if error_seats:
            return render(request, 'movies/seat_selection.html', {
                'theaters': theater,
                'seats': seats,
                'error': f'Seats already booked: {", ".join(error_seats)}',
            })
        messages.success(request, 'Booking confirmed! Check your email.')
        return redirect('profile')

    return render(request, 'movies/seat_selection.html', {'theaters': theater, 'seats': seats})


@login_required
def admin_dashboard(request):
    """Admin dashboard with analytics - only for superusers or staff."""
    # Allow only superusers or staff members
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('home')
    
    try:
        total_revenue = Booking.objects.filter(payment_status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Get popular movies by counting bookings
        popular_movies = Booking.objects.values('movie').annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')[:5]
        
        # Enhance with movie details
        popular_movie_ids = [item['movie'] for item in popular_movies]
        popular_movies = Movie.objects.filter(id__in=popular_movie_ids)

        # Get busiest theaters by counting bookings
        busiest_theaters = Booking.objects.values('theater').annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')[:5]
        
        # Enhance with theater details
        busiest_theater_ids = [item['theater'] for item in busiest_theaters]
        busiest_theaters = Theater.objects.filter(id__in=busiest_theater_ids)

        recent_bookings = Booking.objects.select_related('user', 'movie', 'theater', 'seat').order_by('-booked_at')[:10]

        return render(request, 'admin/dashboard.html', {
            'total_revenue': total_revenue,
            'popular_movies': popular_movies,
            'busiest_theaters': busiest_theaters,
            'recent_bookings': recent_bookings,
        })
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('home')
