from django.contrib import admin
from django.utils.html import format_html
from core.admin import admin_site  # Import our custom analytical admin
from .models import Property, PropertyImage, PropertyDocument, Inquiry, Favorite
from booking.models import Agent  # Import Agent for registration
from django.http import JsonResponse
from django.urls import path
from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- Related Model Registrations ---

@admin.register(Agent, site=admin_site)
class AgentAdmin(admin.ModelAdmin):
    """
    Registered with search_fields to support autocomplete_fields in PropertyAdmin.
    """
    search_fields = ['name', 'email', 'phone']
    list_display = ('name', 'email', 'phone')

# --- Inlines ---

class PropertyImageInline(admin.TabularInline):
    """
    Allows managing multiple images directly on the property page.
    """
    model = PropertyImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto; border-radius: 5px;" />', obj.image.url)
        return ""

class PropertyDocumentInline(admin.TabularInline):
    """
    Manages legal or technical documents for the listing.
    """
    model = PropertyDocument
    extra = 1

# --- Main Property Admin ---

@admin.register(Property, site=admin_site)
class PropertyAdmin(admin.ModelAdmin):
    change_list_template = 'admin/listings/property_analytics.html'
    
    # Enhanced List View: Status is included to satisfy list_editable.
    list_display = (
        'title_display', 
        'price_display', 
        'property_type', 
        'status', 
        'status_badge', 
        'city', 
        'owner', 
        'created_at'
    )
    list_filter = ('status', 'listing_type', 'property_type', 'city', 'owner', 'agent', 'created_at')
    list_editable = ('status',)  
    search_fields = ('title', 'address', 'city', 'description', 'owner__username', 'agent__name')
    
    # Autocomplete optimizes management of large numbers of owners/agents.
    autocomplete_fields = ['owner', 'agent']  
    inlines = [PropertyImageInline, PropertyDocumentInline]
    list_per_page = 20

    # Organized Form Layout for better management experience.
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'listing_type', 'status', 'owner', 'agent')
        }),
        ('Pricing & Financials', {
            'fields': ('price', 'currency', 'price_negotiable')
        }),
        ('Location Details', {
            'fields': ('address', 'city', 'state', 'country', 'zipcode', ('latitude', 'longitude'))
        }),
        ('Specifications', {
            'classes': ('collapse',),
            'fields': ('bedrooms', 'bathrooms', 'area_sqft', 'year_built', 'land_size_acres', 'zoning_type')
        }),
        ('Amenities & Infrastructure', {
            'classes': ('collapse',),
            'fields': (
                ('has_parking', 'parking_spaces'),
                ('has_swimming_pool', 'has_garden'),
                ('has_security', 'has_elevator'),
                ('has_gym', 'has_air_conditioning'),
                ('has_road_access', 'has_electricity'),
                ('has_water_connection', 'is_waterfront')
            )
        }),
    )

    # Bulk Management Actions.
    actions = ['mark_as_sold', 'mark_as_available']

    @admin.action(description='Mark selected properties as Sold')
    def mark_as_sold(self, request, queryset):
        queryset.update(status='sold')

    @admin.action(description='Mark selected properties as Available')
    def mark_as_available(self, request, queryset):
        queryset.update(status='available')
    
    # Custom display methods for Luxury aesthetic.
    def title_display(self, obj):
        return format_html('<b>{}</b>', obj.title)
    title_display.short_description = "Property Title"

    def price_display(self, obj):
        return f"{obj.currency} {obj.price:,.0f}"
    price_display.short_description = "Price"

    def status_badge(self, obj):
        colors = {
            'available': '#28a745', 
            'sold': '#dc3545',      
            'rented': '#ffc107',    
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 50px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = "Status Badge"

    # --- Analytical Part (Retained) ---
    def get_urls(self):
        urls = super().get_urls()
        return [path('analytics/', self.analytics_api, name='analytics')] + urls
    
    def analytics_api(self, request):
        now = datetime.now()
        labels, data = [], []
        for i in range(12):
            month = now - relativedelta(months=i)
            sold = Property.objects.filter(
                status='sold',
                created_at__year=month.year,
                created_at__month=month.month
            ).count()
            labels.append(month.strftime('%b'))
            data.append(sold)
        
        total_sold = Property.objects.filter(status='sold').count()
        revenue = Property.objects.filter(status='sold').aggregate(Sum('price'))['price__sum'] or 0
        total = Property.objects.count()
        sell_rate = round((total_sold / total * 100), 1) if total > 0 else 0
        
        return JsonResponse({
            'labels': labels[::-1],
            'data': data[::-1],
            'total_sold': total_sold,
            'total_revenue': float(revenue),
            'sell_rate': sell_rate,
            'available': Property.objects.filter(status='available').count()
        })

# --- Other Models ---

@admin.register(Inquiry, site=admin_site)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('inquirer_name', 'property_link', 'inquirer_email', 'status', 'created_at_formatted')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('inquirer_name', 'inquirer_email', 'message')
    readonly_fields = ('created_at',)

    def property_link(self, obj):
        return obj.property.title if obj.property else "General Inquiry"
    property_link.short_description = "Interested In"

    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%b %d, %Y, %H:%M")
    created_at_formatted.short_description = "Received"

@admin.register(Favorite, site=admin_site)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'property__title')