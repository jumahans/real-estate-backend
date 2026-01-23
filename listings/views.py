from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import math

from .models import Property, Inquiry, Favorite
from .forms import InquiryForm
from booking.forms import BookingForm

# ==========================================
# 1. PUBLIC BROWSING
# ==========================================

def property_list(request):
    """Main public browsing page."""
    queryset = Property.objects.filter(status='available')\
        .select_related('owner')\
        .prefetch_related('images')\
        .order_by('-created_at')
    
    # Efficient Favorite Check
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, property=OuterRef('pk'))
        queryset = queryset.annotate(is_favorited=Exists(is_fav))
    
    # Search & Filters
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(city__icontains=query))
    
    if request.GET.get('property_type'):
        queryset = queryset.filter(property_type=request.GET.get('property_type'))
    if request.GET.get('city'):
        queryset = queryset.filter(city__iexact=request.GET.get('city'))
    if request.GET.get('min_price'):
        queryset = queryset.filter(price__gte=request.GET.get('min_price'))
    if request.GET.get('max_price'):
        queryset = queryset.filter(price__lte=request.GET.get('max_price'))
        
    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['price', '-price', 'created_at', '-created_at']:
        queryset = queryset.order_by(sort_by)

    paginator = Paginator(queryset, 12) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'properties': page_obj,
        'total_count': queryset.count(),
        'property_types': Property.PROPERTY_TYPES,
        'cities': Property.objects.filter(status='available').values_list('city', flat=True).distinct(),
    }
    return render(request, 'properties/property_list.html', context)

def property_search(request):
    return property_list(request)

def property_detail(request, pk):
    """Public property detail page."""
    property_obj = get_object_or_404(
        Property.objects.select_related('owner').prefetch_related('images'), 
        pk=pk
    )
    
    # View Counter (Session based)
    session_key = f'viewed_property_{pk}'
    if not request.session.get(session_key, False):
        # property_obj.views.create(...) # If you track analytics
        request.session[session_key] = True

    # Inquiry Form Logic
    if request.method == 'POST' and 'submit_inquiry' in request.POST:
        inquiry_form = InquiryForm(request.POST)
        if inquiry_form.is_valid():
            inquiry = inquiry_form.save(commit=False)
            inquiry.property = property_obj
            if request.user.is_authenticated:
                inquiry.user = request.user
            inquiry.save()
            messages.success(request, 'Inquiry sent successfully!')
            return redirect('property_detail', pk=pk)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'inquirer_name': request.user.get_full_name(), 'inquirer_email': request.user.email}
        inquiry_form = InquiryForm(initial=initial)

    # Booking Logic
    booking_form = BookingForm()
    suggested_slots = []
    booking_enabled = hasattr(property_obj, 'booking_settings') and property_obj.booking_settings.is_active
    
    if booking_enabled:
        suggested_slots = property_obj.booking_settings.get_available_slots()

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, property=property_obj).exists()

    context = {
        'property': property_obj,
        'inquiry_form': inquiry_form,
        'booking_form': booking_form,
        'booking_enabled': booking_enabled,
        'suggested_slots': suggested_slots[:4],
        'is_favorited': is_favorited,
        'similar_properties': Property.objects.filter(city=property_obj.city).exclude(pk=pk)[:3]
    }
    return render(request, 'properties/property_detail.html', context)

# ==========================================
# 2. USER ACTIONS (Favorites & Profile)
# ==========================================

@login_required
@require_POST
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    if not created:
        favorite.delete()
        return JsonResponse({'is_favorited': False, 'status': 'success'})
    return JsonResponse({'is_favorited': True, 'status': 'success'})

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('property')
    return render(request, 'properties/favorites.html', {'properties': [f.property for f in favorites]})

@login_required
def inquiry_list(request):
    """User sees inquiries they have SENT."""
    inquiries = Inquiry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'properties/inquiry_list.html', {'inquiries': inquiries})

# ==========================================
# 3. SPECIALTY SEARCH (Maps/Nearby)
# ==========================================

def property_map_search(request):
    properties = Property.objects.filter(status='available')
    return render(request, 'properties/property_map_search.html', {'properties': properties})

def property_nearby_search(request):
    # (Keep your distance logic here)
    return render(request, 'properties/property_nearby.html', {})