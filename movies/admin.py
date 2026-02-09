from django.contrib import admin
from django.contrib import messages
from .models import Movie, Theater, Seat, Booking, SeatReservation
import logging

logger = logging.getLogger(__name__)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'genre', 'language', 'cast']
    list_filter = ['genre', 'language']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'rating', 'genre', 'language', 'cast', 'description')
        }),
        ('Media', {
            'fields': ('image', 'trailer_url'),
            'description': 'Image: OPTIONAL - For Vercel, do NOT upload files (read-only filesystem). Leave blank or use external URLs only.'
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
    list_display = ['name', 'movie', 'time']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']


@admin.register(SeatReservation)
class SeatReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'theater', 'expires_at', 'created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'amount', 'payment_status', 'booked_at']
