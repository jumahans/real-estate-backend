from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking, BookingSettings
from .forms import BookingForm
from listings.models import Property

@login_required
def create_booking(request, property_pk):
    """
    Process the booking form submission from the property detail page.
    """
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.listing = property_obj
            
            # --- 1. VALIDATION: Check for past dates ---
            if booking.start_datetime < timezone.now():
                messages.error(request, "You cannot book a time in the past.")
                return redirect('property_detail', pk=property_pk)

            # --- 2. VALIDATION: Check for conflicts ---
            # Calculate end time based on settings (default 1 hour if no settings)
            duration = 60
            if hasattr(property_obj, 'booking_settings'):
                duration = property_obj.booking_settings.slot_duration
            
            # Simple conflict check: Is there any confirmed booking at this exact start time?
            # (For a real production app, you'd check overlapping ranges)
            conflict = Booking.objects.filter(
                listing=property_obj,
                status='confirmed',
                start_datetime=booking.start_datetime
            ).exists()
            
            if conflict:
                messages.error(request, "Sorry, this slot is already booked. Please choose another.")
                return redirect('property_detail', pk=property_pk)

            # --- 3. SUCCESS ---
            booking.save()
            messages.success(request, 'Booking request sent! You can view it in your dashboard.')
            return redirect('my_bookings')
    
    # If not POST, just redirect back to detail
    return redirect('property_detail', pk=property_pk)

@login_required
def my_bookings(request):
    """List of user's bookings."""
    now = timezone.now()
    # Split into Upcoming and Past
    upcoming = Booking.objects.filter(user=request.user, start_datetime__gte=now).order_by('start_datetime')
    past = Booking.objects.filter(user=request.user, start_datetime__lt=now).order_by('-start_datetime')
    
    return render(request, 'bookings/my_bookings.html', {
        'upcoming_bookings': upcoming,
        'past_bookings': past
    })

@login_required
def cancel_booking(request, pk):
    """Allow user to cancel their own booking."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.status != 'cancelled':
        booking.status = 'cancelled'
        booking.save()
        messages.info(request, "Booking cancelled successfully.")
    
    return redirect('my_bookings')