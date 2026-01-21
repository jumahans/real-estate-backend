from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum, F
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from math import radians, cos, sin, asin, sqrt
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .models import (
    Property, PropertyImage, PropertyDocument, PropertyView,
    PricingHistory, Inquiry, Favorite
)
from .forms import (
    PropertyCreateForm, PropertyUpdateForm, PropertySearchForm,
    PropertyImageForm, PropertyDocumentForm, InquiryForm
)


# ============= PROPERTY LISTING VIEWS =============

def property_list(request):
    """Display all properties with search and filters"""
    properties = Property.objects.filter(status='available').prefetch_related('images')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Filters
    property_type = request.GET.get('property_type')
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    listing_type = request.GET.get('listing_type')
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    
    city = request.GET.get('city')
    if city:
        properties = properties.filter(city__iexact=city)
    
    min_price = request.GET.get('min_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    min_bedrooms = request.GET.get('min_bedrooms')
    if min_bedrooms:
        properties = properties.filter(bedrooms__gte=min_bedrooms)
    
    # Land-specific filters
    is_waterfront = request.GET.get('is_waterfront')
    if is_waterfront == 'true':
        properties = properties.filter(is_waterfront=True)
    
    zoning_type = request.GET.get('zoning_type')
    if zoning_type:
        properties = properties.filter(zoning_type=zoning_type)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    properties = properties.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique cities for filter dropdown
    cities = Property.objects.values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'properties': page_obj,
        'search_query': search_query,
        'cities': cities,
        'property_types': Property.PROPERTY_TYPES,
        'listing_types': Property.LISTING_TYPE,
        'zoning_types': Property.ZONING_TYPES,
        'total_count': properties.count(),
    }
    
    return render(request, 'properties/property_list.html', context)


def property_detail(request, pk):
    """Display single property details"""
    property_obj = get_object_or_404(
        Property.objects.prefetch_related('images', 'documents', 'price_history'),
        pk=pk
    )
    
    # Track view
    PropertyView.objects.create(
        property=property_obj,
        viewer_ip=get_client_ip(request),
        user=request.user if request.user.is_authenticated else None,
        session_id=request.session.session_key
    )
    
    # Get similar properties
    if property_obj.is_land:
        similar_properties = Property.objects.filter(
            property_type=property_obj.property_type,
            city=property_obj.city,
            status='available'
        ).exclude(pk=property_obj.pk)[:6]
    else:
        price_min = property_obj.price * Decimal('0.8')
        price_max = property_obj.price * Decimal('1.2')
        similar_properties = Property.objects.filter(
            property_type=property_obj.property_type,
            city=property_obj.city,
            bedrooms=property_obj.bedrooms,
            status='available',
            price__gte=price_min,
            price__lte=price_max
        ).exclude(pk=property_obj.pk)[:6]
    
    # Get statistics
    view_count = property_obj.views.count()
    view_count_30_days = property_obj.views.filter(
        viewed_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    inquiry_count = property_obj.inquiries.count()
    days_on_market = (timezone.now().date() - property_obj.created_at.date()).days
    
    # Check if user has favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            property=property_obj
        ).exists()
    
    # Inquiry form
    inquiry_form = InquiryForm()
    
    context = {
        'property': property_obj,
        'similar_properties': similar_properties,
        'view_count': view_count,
        'view_count_30_days': view_count_30_days,
        'inquiry_count': inquiry_count,
        'days_on_market': days_on_market,
        'is_favorited': is_favorited,
        'inquiry_form': inquiry_form,
    }
    
    return render(request, 'properties/property_detail.html', context)


#property search views

def property_search(request):
    """Advanced property search"""
    properties = Property.objects.filter(status='available')
    
    if request.method == 'GET':
        form = PropertySearchForm(request.GET)
        if form.is_valid():
            # Apply all filters from form
            if form.cleaned_data.get('property_type'):
                properties = properties.filter(property_type=form.cleaned_data['property_type'])
            
            if form.cleaned_data.get('listing_type'):
                properties = properties.filter(listing_type=form.cleaned_data['listing_type'])
            
            if form.cleaned_data.get('min_price'):
                properties = properties.filter(price__gte=form.cleaned_data['min_price'])
            
            if form.cleaned_data.get('max_price'):
                properties = properties.filter(price__lte=form.cleaned_data['max_price'])
            
            if form.cleaned_data.get('min_bedrooms'):
                properties = properties.filter(bedrooms__gte=form.cleaned_data['min_bedrooms'])
            
            if form.cleaned_data.get('max_bedrooms'):
                properties = properties.filter(bedrooms__lte=form.cleaned_data['max_bedrooms'])
            
            if form.cleaned_data.get('min_bathrooms'):
                properties = properties.filter(bathrooms__gte=form.cleaned_data['min_bathrooms'])
            
            if form.cleaned_data.get('city'):
                properties = properties.filter(city__icontains=form.cleaned_data['city'])
            
            if form.cleaned_data.get('state'):
                properties = properties.filter(state__icontains=form.cleaned_data['state'])
            
            # Land-specific filters
            if form.cleaned_data.get('min_land_acres'):
                properties = properties.filter(land_size_acres__gte=form.cleaned_data['min_land_acres'])
            
            if form.cleaned_data.get('max_land_acres'):
                properties = properties.filter(land_size_acres__lte=form.cleaned_data['max_land_acres'])
            
            if form.cleaned_data.get('zoning_type'):
                properties = properties.filter(zoning_type=form.cleaned_data['zoning_type'])
            
            if form.cleaned_data.get('topography'):
                properties = properties.filter(topography=form.cleaned_data['topography'])
            
            # Boolean filters
            if form.cleaned_data.get('is_waterfront'):
                properties = properties.filter(is_waterfront=True)
            
            if form.cleaned_data.get('has_electricity'):
                properties = properties.filter(has_electricity=True)
            
            if form.cleaned_data.get('has_water_access'):
                properties = properties.filter(has_water_access=True)
            
            if form.cleaned_data.get('subdivision_potential'):
                properties = properties.filter(subdivision_potential=True)
            
            if form.cleaned_data.get('has_parking'):
                properties = properties.filter(has_parking=True)
            
            if form.cleaned_data.get('has_swimming_pool'):
                properties = properties.filter(has_swimming_pool=True)
    else:
        form = PropertySearchForm()
    
    # Pagination
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'properties': page_obj,
        'total_count': properties.count(),
    }
    
    return render(request, 'properties/property_search.html', context)




# ============= INQUIRY VIEWS =============

def property_inquiry_create(request, property_pk):
    """Create inquiry for property"""
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = property_obj
            
            if request.user.is_authenticated:
                inquiry.user = request.user
                inquiry.inquirer_email = request.user.email
            
            inquiry.save()
            
            messages.success(request, 'Your inquiry has been sent successfully!')
            return redirect('property_detail', pk=property_pk)
    else:
        # Pre-fill form if user is authenticated
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'inquirer_name': request.user.get_full_name() or request.user.username,
                'inquirer_email': request.user.email,
            }
        form = InquiryForm(initial=initial)
    
    context = {
        'form': form,
        'property': property_obj,
    }
    
    return render(request, 'properties/inquiry_form.html', context)


#@login_required
def inquiry_list(request):
    """View all inquiries for user's properties"""
    inquiries = Inquiry.objects.filter(
        property__owner=request.user
    ).select_related('property').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        inquiries = inquiries.filter(status=status)
    
    # Pagination
    paginator = Paginator(inquiries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'inquiries': page_obj,
        'status_choices': Inquiry._meta.get_field('status').choices,
    }
    
    return render(request, 'properties/inquiry_list.html', context)


#@login_required
def inquiry_detail(request, pk):
    """View inquiry details"""
    inquiry = get_object_or_404(Inquiry, pk=pk)
    
    # Check permission
    if inquiry.property.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        # Update status
        new_status = request.POST.get('status')
        if new_status:
            inquiry.status = new_status
            if new_status == 'contacted' and not inquiry.responded_at:
                inquiry.responded_at = timezone.now()
            inquiry.save()
            messages.success(request, 'Inquiry status updated!')
    
    context = {
        'inquiry': inquiry,
        'status_choices': Inquiry._meta.get_field('status').choices,
    }
    
    return render(request, 'properties/inquiry_detail.html', context)


#fabourite properties

#@login_required
def property_favorite_toggle(request, property_pk):
    """Toggle favorite for property"""
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        property=property_obj
    )
    
    if not created:
        favorite.delete()
        messages.success(request, 'Property removed from favorites!')
    else:
        messages.success(request, 'Property added to favorites!')
    
    return redirect('property_detail', pk=property_pk)


#@login_required
def favorite_list(request):
    """View user's favorite properties"""
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('property').prefetch_related('property__images')
    
    # Pagination
    paginator = Paginator(favorites, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'favorites': page_obj,
    }
    
    return render(request, 'properties/favorite_list.html', context)


#property management views

#@login_required
def property_dashboard(request):
    """Owner's property management dashboard"""
    properties = Property.objects.filter(owner=request.user).prefetch_related('images', 'views', 'inquiries')
    
    # Statistics
    total_properties = properties.count()
    available_properties = properties.filter(status='available').count()
    sold_properties = properties.filter(status='sold').count()
    rented_properties = properties.filter(status='rented').count()
    
    # Total value
    total_value = properties.aggregate(total=Sum('price'))['total'] or 0
    
    # Recent inquiries
    recent_inquiries = Inquiry.objects.filter(
        property__owner=request.user
    ).select_related('property').order_by('-created_at')[:10]
    
    # Most viewed properties
    most_viewed = properties.annotate(
        view_count=Count('views')
    ).order_by('-view_count')[:5]
    
    context = {
        'properties': properties,
        'total_properties': total_properties,
        'available_properties': available_properties,
        'sold_properties': sold_properties,
        'rented_properties': rented_properties,
        'total_value': total_value,
        'recent_inquiries': recent_inquiries,
        'most_viewed': most_viewed,
    }
    
    return render(request, 'properties/dashboard.html', context)


#@login_required
def property_analytics(request, pk):
    """View analytics for specific property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    
    # View statistics
    total_views = property_obj.views.count()
    unique_ips = property_obj.views.values('viewer_ip').distinct().count()
    
    # Views over time
    thirty_days_ago = timezone.now() - timedelta(days=30)
    views_30_days = property_obj.views.filter(viewed_at__gte=thirty_days_ago).count()
    
    seven_days_ago = timezone.now() - timedelta(days=7)
    views_7_days = property_obj.views.filter(viewed_at__gte=seven_days_ago).count()
    
    # Inquiries
    total_inquiries = property_obj.inquiries.count()
    new_inquiries = property_obj.inquiries.filter(status='new').count()
    
    # Favorites
    favorite_count = property_obj.favorited_by.count()
    
    # Days on market
    days_on_market = (timezone.now().date() - property_obj.created_at.date()).days
    
    # Price history
    price_history = property_obj.price_history.all()[:10]
    
    context = {
        'property': property_obj,
        'total_views': total_views,
        'unique_ips': unique_ips,
        'views_30_days': views_30_days,
        'views_7_days': views_7_days,
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'favorite_count': favorite_count,
        'days_on_market': days_on_market,
        'price_history': price_history,
    }
    
    return render(request, 'properties/property_analytics.html', context)


# ============= FEATURED & SPECIAL VIEWS =============

def property_featured(request):
    """Display featured properties (most viewed)"""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    properties = Property.objects.filter(
        status='available'
    ).annotate(
        recent_views=Count('views', filter=Q(views__viewed_at__gte=thirty_days_ago))
    ).order_by('-recent_views')[:20]
    
    context = {
        'properties': properties,
        'title': 'Featured Properties',
    }
    
    return render(request, 'properties/property_list.html', context)


def property_latest(request):
    """Display latest properties"""
    properties = Property.objects.filter(
        status='available'
    ).order_by('-created_at')[:20]
    
    context = {
        'properties': properties,
        'title': 'Latest Properties',
    }
    
    return render(request, 'properties/property_list.html', context)


def property_by_type(request, property_type):
    """Display properties by type"""
    properties = Property.objects.filter(
        property_type=property_type,
        status='available'
    ).prefetch_related('images')
    
    # Pagination
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'property_type': property_type,
        'title': f'{dict(Property.PROPERTY_TYPES).get(property_type)} Properties',
    }
    
    return render(request, 'properties/property_list.html', context)


def property_by_city(request, city):
    """Display properties by city"""
    properties = Property.objects.filter(
        city__iexact=city,
        status='available'
    ).prefetch_related('images')
    
    # Pagination
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'city': city,
        'title': f'Properties in {city}',
    }
    
    return render(request, 'properties/property_list.html', context)


# ============= HELPER FUNCTIONS =============

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two points on earth (in km)"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km



@require_http_methods(["GET"])
def property_map_search(request):
    """Search properties by map bounds and location"""
    properties = Property.objects.filter(status='available')
    
    # Get map bounds from request
    ne_lat = request.GET.get('ne_lat')
    ne_lng = request.GET.get('ne_lng')
    sw_lat = request.GET.get('sw_lat')
    sw_lng = request.GET.get('sw_lng')
    
    # Filter by map bounds if provided
    if all([ne_lat, ne_lng, sw_lat, sw_lng]):
        properties = properties.filter(
            latitude__lte=Decimal(ne_lat),
            latitude__gte=Decimal(sw_lat),
            longitude__lte=Decimal(ne_lng),
            longitude__gte=Decimal(sw_lng)
        )
    
    # Search by location query (city, address, etc.)
    location_query = request.GET.get('location', '')
    if location_query:
        properties = properties.filter(
            Q(city__icontains=location_query) |
            Q(address__icontains=location_query) |
            Q(state__icontains=location_query) |
            Q(neighborhood__icontains=location_query) |
            Q(formatted_address__icontains=location_query)
        )
    
    # Apply other filters (price, bedrooms, etc.)
    property_type = request.GET.get('property_type')
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    min_price = request.GET.get('min_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    # Return JSON for map markers
    if request.GET.get('format') == 'json':
        properties_data = []
        for prop in properties[:500]:  # Limit for performance
            primary_image = prop.images.filter(is_primary=True).first()
            if not primary_image:
                primary_image = prop.images.first()
            
            properties_data.append({
                'id': prop.pk,
                'title': prop.title,
                'price': float(prop.price),
                'currency': prop.currency,
                'property_type': prop.get_property_type_display(),
                'listing_type': prop.get_listing_type_display(),
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
                'land_size_acres': float(prop.land_size_acres) if prop.land_size_acres else None,
                'latitude': float(prop.latitude),
                'longitude': float(prop.longitude),
                'address': prop.address,
                'city': prop.city,
                'image_url': primary_image.image.url if primary_image else None,
                'url': reverse('property_detail', kwargs={'pk': prop.pk})
            })
        
        return JsonResponse({'properties': properties_data})
    
    # Return template view
    context = {
        'properties': properties,
        'location_query': location_query,
    }
    
    return render(request, 'properties/property_map_search.html', context)


def property_nearby_search(request):
    """Search properties within radius of a location"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius_miles = request.GET.get('radius', 10)  # Default 10 miles
    
    if not lat or not lng:
        return JsonResponse({'error': 'Latitude and longitude required'}, status=400)
    
    try:
        lat = float(lat)
        lng = float(lng)
        radius_miles = float(radius_miles)
    except ValueError:
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)
    
    # Get all available properties
    properties = Property.objects.filter(status='available')
    
    # Calculate distance and filter
    nearby_properties = []
    for prop in properties:
        distance = haversine(
            lng, lat,
            float(prop.longitude), float(prop.latitude)
        )
        distance_miles = distance * 0.621371  # Convert km to miles
        
        if distance_miles <= radius_miles:
            nearby_properties.append({
                'property': prop,
                'distance_miles': round(distance_miles, 2)
            })
    
    # Sort by distance
    nearby_properties.sort(key=lambda x: x['distance_miles'])
    
    if request.GET.get('format') == 'json':
        data = []
        for item in nearby_properties[:100]:
            prop = item['property']
            primary_image = prop.images.filter(is_primary=True).first()
            
            data.append({
                'id': prop.pk,
                'title': prop.title,
                'price': float(prop.price),
                'distance_miles': item['distance_miles'],
                'latitude': float(prop.latitude),
                'longitude': float(prop.longitude),
                'image_url': primary_image.image.url if primary_image else None,
                'url': reverse('property_detail', kwargs={'pk': prop.pk})
            })
        
        return JsonResponse({'properties': data})
    
    context = {
        'nearby_properties': nearby_properties,
        'search_lat': lat,
        'search_lng': lng,
        'radius': radius_miles,
    }
    
    return render(request, 'properties/property_nearby.html', context)



