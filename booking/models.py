from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from core.models import TimeStampedModel
from listings.models import Property as Listing

User = get_user_model()

class BookingSettings(TimeStampedModel):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='booking_settings')
    max_viewers_per_slot = models.PositiveIntegerField(default=5)
    slot_duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    start_hour = models.IntegerField(default=9)
    end_hour = models.IntegerField(default=18)
    cancellation_window_hours = models.PositiveIntegerField(default=24)

    def __str__(self):
        return f"Settings for: {self.listing.title}"

    def get_available_slots(self):
        now = timezone.now()
        slots = []
        current_date = now.date()
        
        for day_offset in range(7):
            for hour in range(self.start_hour, self.end_hour):
                start = timezone.make_aware(timezone.datetime(
                    current_date.year, current_date.month, current_date.day, hour, 0, 0
                ))
                if start < now: continue
                
                end = start + timedelta(minutes=self.slot_duration_minutes)
                count = Booking.objects.filter(
                    listing=self.listing,
                    start_datetime__lt=end,
                    end_datetime__gt=start,
                    status__in=['pending', 'confirmed']
                ).count()
                
                if count < self.max_viewers_per_slot:
                    slots.append({'start': start, 'end': end, 'available': self.max_viewers_per_slot - count})
            
            current_date += timedelta(days=1)
            if len(slots) >= 10: break
        return slots

class Booking(TimeStampedModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_datetime']

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        if self.listing and not self.end_datetime:
            self.end_datetime = self.start_datetime + timedelta(minutes=60)
        super().save(*args, **kwargs)