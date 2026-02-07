from django.contrib import admin
from .models import Movie, Theater, Seat, Booking, SeatReservation

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
            'description': 'Image: Optional. For Vercel, use external image URLs. Uploads do not persist.'
        }),
        ('Pricing', {
            'fields': ('ticket_price',)
        }),
    )


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
