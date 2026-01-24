from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from core.models import TimeStampedModel

User = get_user_model()

class BookingSettings(TimeStampedModel):
    listing = models.OneToOneField('listings.Property', on_delete=models.CASCADE, related_name='booking_settings')
    max_viewers_per_slot = models.PositiveIntegerField(default=5)
    slot_duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    start_hour = models.IntegerField(default=9)
    end_hour = models.IntegerField(default=18)
    cancellation_window_hours = models.PositiveIntegerField(default=24)

    def __str__(self):
        return f"Settings for: {self.listing.title}"

    # ... get_available_slots method unchanged ...

class Booking(TimeStampedModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey('listings.Property', on_delete=models.CASCADE, related_name='bookings')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_datetime']

    def save(self, *args, **kwargs):
        if self.listing and not self.end_datetime:
            self.end_datetime = self.start_datetime + timedelta(minutes=60)
        super().save(*args, **kwargs)

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return self.name