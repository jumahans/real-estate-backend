from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileUpdateForm

def register(request):
    """
    Handles new user registration and auto-creates their profile.
    """
    if request.user.is_authenticated:
        return redirect('property_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = user.username
            messages.success(request, f'Account created for {username}! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})

@login_required
def profile_view(request):
    """
    Allows logged-in users to update their contact info (Phone, Address).
    """
    if request.method == 'POST':
        # We pass 'user' to the form to handle email/name updates on the User model
        form = ProfileUpdateForm(request.POST, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile details have been updated.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile, user=request.user)
    
    return render(request, 'core/profile.html', {'form': form})