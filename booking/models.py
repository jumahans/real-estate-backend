from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

User = get_user_model()

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Property(models.Model):
    TYPE_CHOICES = [('viewing', 'Viewing'), ('unit', 'Unit')]
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    max_viewers = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    cancellation_window_hours = models.PositiveIntegerField(default=24)

    def __str__(self):
        return self.title

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    agents = models.ManyToManyField(Agent, blank=True)  # Renamed for clarity
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_ref = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['property', 'start_datetime', 'status']),
        ]

    def overlaps_with(self, other):
        return (self.start_datetime < other.end_datetime and 
                self.end_datetime > other.start_datetime)

    def clean(self):
        now = timezone.now()
        if not self.start_datetime or self.start_datetime < now:  # Add null check
            raise ValidationError('Start datetime required and cannot be past.')
        if not self.end_datetime or self.start_datetime >= self.end_datetime:
            raise ValidationError('End must be after start.')
        
        overlaps = self.property.bookings.filter(
            Q(start_datetime__lt=self.end_datetime) &
            Q(end_datetime__gt=self.start_datetime) &
            Q(status__in=['pending', 'confirmed'])
        ).exclude(pk=self.pk)
        
        if self.property.type == 'viewing':
            if overlaps.count() >= self.property.max_viewers:
                raise ValidationError(f'Max {self.property.max_viewers} viewers.')
        else:
            if overlaps.exists():
                raise ValidationError('Unit already reserved.')
        
        # Fixed: Same-day double-book check (per your comment)
        if self.property.bookings.filter(
            user=self.user, property=self.property,
            start_datetime__date=self.start_datetime.date(),
            status__in=['pending', 'confirmed']
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Cannot book same day twice.')

        if (self.status == 'cancelled' and 
            now > self.start_datetime - timedelta(hours=self.property.cancellation_window_hours)):
            raise ValidationError('Cannot cancel within window.')

    def save(self, *args, **kwargs):
        if self.pk:
            old = Booking.objects.get(pk=self.pk)
            if old.version != self.version:
                raise ValidationError('Concurrent update detected.')
            # Inactivation logic
            if old.status != self.status:
                if self.status == 'confirmed':
                    self.property.is_active = False
                    self.property.save()
                elif self.status in ['cancelled', 'completed']:
                    self.property.is_active = True
                    self.property.save()
            self.version = old.version + 1
        #else:
            # New booking: Auto-add property agent if available
           # if self.property.agent and self.property.agent not in self.agents.all():
                # self.agents.add(self.property.agent)
            # elif Agent.objects.exists() and not self.agents.exists():
                # self.agents.add(Agent.objects.first())
        super().save(*args, **kwargs)
