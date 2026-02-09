from django.contrib import admin
from django.contrib import messages
from django import forms
from .models import Movie, Theater, Seat, Booking, SeatReservation
import logging

logger = logging.getLogger(__name__)


class TheaterForm(forms.ModelForm):
    """Custom form for Theater that allows creating seats layout."""
    rows = forms.IntegerField(
        min_value=1, 
        max_value=26,  # A-Z
        required=False,
        help_text="Number of rows (A, B, C, etc.)"
    )
    columns = forms.IntegerField(
        min_value=1,
        max_value=100,
        required=False,
        help_text="Number of columns (1, 2, 3, etc.)"
    )
    
    class Meta:
        model = Theater
        fields = ['name', 'movie', 'time']
    
    def clean(self):
        cleaned_data = super().clean()
        rows = cleaned_data.get('rows')
        columns = cleaned_data.get('columns')
        
        if (rows and not columns) or (not rows and columns):
            raise forms.ValidationError(
                "Please enter both rows AND columns, or leave both empty."
            )
        return cleaned_data


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'genre', 'language', 'cast']
    list_filter = ['genre', 'language']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'rating', 'genre', 'language', 'cast', 'description')
        }),
        ('Media', {
            'fields': ('external_image_url', 'image', 'trailer_url'),
            'description': 'For Vercel deployment: Paste image URL in "External Image URL" field. Do NOT upload files (read-only filesystem).'
        }),
        ('Pricing', {
            'fields': ('ticket_price',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            messages.success(request, f'Movie "{obj.name}" saved successfully!')
        except Exception as e:
            error_msg = str(e)
            logger.error(f'Error saving movie: {error_msg}', exc_info=True)
            
            # Handle read-only filesystem errors on Vercel
            if 'Read-only file system' in error_msg or 'Permission denied' in error_msg:
                # Clear the image field and try again
                if hasattr(obj, 'image') and obj.image:
                    obj.image = None
                    try:
                        super().save_model(request, obj, form, change)
                        messages.warning(request, f'Movie "{obj.name}" saved but image upload failed (Vercel read-only filesystem). Use external image URLs instead.')
                        return
                    except Exception as e2:
                        logger.error(f'Error saving movie after clearing image: {str(e2)}', exc_info=True)
                        messages.error(request, f'Error saving movie: {str(e2)}')
                        raise
            
            messages.error(request, f'Error saving movie: {error_msg}')
            raise


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    form = TheaterForm
    list_display = ['name', 'movie', 'time', 'seat_count']
    
    def seat_count(self, obj):
        return obj.seats.count()
    seat_count.short_description = 'Total Seats'
    
    def save_model(self, request, obj, form, change):
        """Save theater and auto-generate seats if rows/columns provided."""
        try:
            super().save_model(request, obj, form, change)
            
            rows = form.cleaned_data.get('rows')
            columns = form.cleaned_data.get('columns')
            
            # Auto-generate seats if layout provided
            if rows and columns:
                # Delete existing seats to regenerate
                obj.seats.all().delete()
                
                # Generate seat layout
                seat_objects = []
                for row_num in range(rows):
                    row_letter = chr(65 + row_num)  # A, B, C, etc.
                    for col_num in range(1, columns + 1):
                        seat_number = f"{row_letter}{col_num}"
                        seat_objects.append(
                            Seat(theater=obj, seat_number=seat_number, is_booked=False)
                        )
                
                # Bulk create seats
                Seat.objects.bulk_create(seat_objects)
                messages.success(
                    request, 
                    f'Theater "{obj.name}" created with {rows}x{columns} = {rows * columns} seats!'
                )
            else:
                messages.success(request, f'Theater "{obj.name}" saved successfully!')
        except Exception as e:
            logger.error(f'Error saving theater: {str(e)}', exc_info=True)
            messages.error(request, f'Error saving theater: {str(e)}')
            raise


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']
    list_filter = ['theater', 'is_booked']
    ordering = ['theater', 'seat_number']
    change_list_template = 'admin/seat_changelist.html'
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view that organizes seats by row."""
        response = super().changelist_view(request, extra_context)
        
        if hasattr(response, 'context_data'):
            # Get all theaters
            theaters = Theater.objects.all()
            theater_seats = {}
            
            for theater in theaters:
                seats = theater.seats.all().order_by('seat_number')
                rows = {}
                
                # Group seats by row letter
                for seat in seats:
                    row_letter = seat.seat_number[0] if seat.seat_number else 'X'
                    if row_letter not in rows:
                        rows[row_letter] = []
                    rows[row_letter].append(seat)
                
                theater_seats[theater.name] = rows
            
            response.context_data['theater_seats'] = theater_seats
        
        return response


@admin.register(SeatReservation)
class SeatReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'theater', 'expires_at', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'amount', 'payment_status', 'booked_at']
