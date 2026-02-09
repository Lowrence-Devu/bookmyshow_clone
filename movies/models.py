from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Genre and Language choices for filtering
GENRE_CHOICES = [
    ('action', 'Action'),
    ('comedy', 'Comedy'),
    ('drama', 'Drama'),
    ('horror', 'Horror'),
    ('romance', 'Romance'),
    ('sci-fi', 'Sci-Fi'),
    ('thriller', 'Thriller'),
    ('animation', 'Animation'),
    ('other', 'Other'),
]

LANGUAGE_CHOICES = [
    ('hindi', 'Hindi'),
    ('english', 'English'),
    ('tamil', 'Tamil'),
    ('telugu', 'Telugu'),
    ('malayalam', 'Malayalam'),
    ('kannada', 'Kannada'),
    ('bengali', 'Bengali'),
    ('other', 'Other'),
]


class Movie(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/", blank=True, null=True)
    external_image_url = models.URLField(blank=True, null=True, help_text="For Vercel: Paste external image URL here instead of uploading (e.g., from Imgur, Cloudinary)")
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    cast = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='other')
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='english')
    trailer_url = models.URLField(blank=True, null=True, help_text="YouTube trailer URL")
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=150.00)

    def __str__(self):
        return self.name

    def get_youtube_embed_url(self):
        """Convert YouTube URL to embed format."""
        if not self.trailer_url:
            return None
        url = self.trailer_url
        if 'youtube.com/watch?v=' in url:
            vid = url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            vid = url.split('youtu.be/')[1].split('?')[0]
        else:
            return url
        return f'https://www.youtube.com/embed/{vid}'


class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.DateTimeField()

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'


class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'


class SeatReservation(models.Model):
    """Temporary seat reservation (5 min timeout) before payment."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['seat', 'theater']

    def __str__(self):
        return f'{self.seat.seat_number} reserved by {self.user.username} until {self.expires_at}'


class Booking(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name='booking')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='completed')
    payment_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'