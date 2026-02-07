# Generated manually for feature additions

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='genre',
            field=models.CharField(choices=[('action', 'Action'), ('comedy', 'Comedy'), ('drama', 'Drama'), ('horror', 'Horror'), ('romance', 'Romance'), ('sci-fi', 'Sci-Fi'), ('thriller', 'Thriller'), ('animation', 'Animation'), ('other', 'Other')], default='other', max_length=50),
        ),
        migrations.AddField(
            model_name='movie',
            name='language',
            field=models.CharField(choices=[('hindi', 'Hindi'), ('english', 'English'), ('tamil', 'Tamil'), ('telugu', 'Telugu'), ('malayalam', 'Malayalam'), ('kannada', 'Kannada'), ('bengali', 'Bengali'), ('other', 'Other')], default='english', max_length=50),
        ),
        migrations.AddField(
            model_name='movie',
            name='trailer_url',
            field=models.URLField(blank=True, help_text='YouTube trailer URL', null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='ticket_price',
            field=models.DecimalField(decimal_places=2, default=150.00, max_digits=8),
        ),
        migrations.AddField(
            model_name='booking',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='completed', max_length=20),
        ),
        migrations.AlterField(
            model_name='booking',
            name='seat',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='movies.seat'),
        ),
        migrations.CreateModel(
            name='SeatReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expires_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.seat')),
                ('theater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.theater')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('seat', 'theater')},
            },
        ),
    ]
