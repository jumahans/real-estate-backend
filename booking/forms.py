from django import forms
from django.utils import timezone
from .models import Booking, BookingSettings

class BookingForm(forms.ModelForm):
    """
    Form for clients to book a viewing slot.
    Uses HTML5 datetime-local input for better UX on mobile.
    """
    class Meta:
        model = Booking
        fields = ['start_datetime', 'notes']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')  # Prevent past selection in UI
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests? (e.g., "I will be 5 mins late")'
            }),
        }
        labels = {
            'start_datetime': 'Preferred Date & Time',
            'notes': 'Additional Notes'
        }

    def clean_start_datetime(self):
        """Ensure date is not in the past (Backend validation)"""
        start_datetime = self.cleaned_data['start_datetime']
        if start_datetime < timezone.now():
            raise forms.ValidationError("You cannot book a slot in the past.")
        return start_datetime

class BookingSettingsForm(forms.ModelForm):
    """
    Form for the Agent to configure booking rules for a specific property.
    e.g., Define working hours, slot duration.
    """
    class Meta:
        model = BookingSettings
        fields = [
            'max_viewers_per_slot', 'slot_duration_minutes', 
            'start_hour', 'end_hour', 
            'cancellation_window_hours', 'is_active'
        ]
        widgets = {
            'max_viewers_per_slot': forms.NumberInput(attrs={'class': 'form-control'}),
            'slot_duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'step': '15'}),
            'start_hour': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 23}),
            'end_hour': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 23}),
            'cancellation_window_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'start_hour': 'Hour of the day (0-23) when viewings start (e.g., 9 for 9 AM)',
            'end_hour': 'Hour of the day (0-23) when viewings end (e.g., 17 for 5 PM)',
        }