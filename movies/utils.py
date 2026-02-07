"""Utility functions for movies app."""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_booking_confirmation_email(user, movie_name, theater_name, show_time, seats, amount, booking_id):
    """Send email confirmation after successful booking."""
    subject = f'Your BookMySeat Booking Confirmation - {movie_name}'
    html_content = render_to_string('emails/booking_confirmation.html', {
        'user': user,
        'movie_name': movie_name,
        'theater_name': theater_name,
        'show_time': show_time,
        'seats': seats,
        'amount': amount,
        'booking_id': booking_id,
    })
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
        to=[user.email] if user.email else [],
        fail_silently=True,
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)
