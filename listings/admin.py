from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Property, PropertyImage, PropertyDocument, 
    PropertyView, PricingHistory, Inquiry, Favorite
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'image_type', 'is_primary')
    readonly_fields = ('uploaded_at',)


class PropertyDocumentInline(admin.TabularInline):
    model = PropertyDocument
    extra = 0
    fields = ('document_type', 'title', 'document', 'is_public', 'uploaded_by')
    readonly_fields = ('uploaded_at',)


class PricingHistoryInline(admin.TabularInline):
    model = PricingHistory
    extra = 0
    fields = ('old_price', 'new_price', 'changed_by', 'reason', 'changed_at')
    readonly_fields = ('changed_at',)
    can_delete = False


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'property_type', 'listing_type', 'status', 
        'display_price', 'city', 'country', 'bedrooms', 
        'land_size_acres', 'view_count', 'inquiry_count', 
        'created_at'
    )
    list_filter = (
        'status', 'property_type', 'listing_type', 'country', 
        'city', 'zoning_type', 'is_waterfront', 'has_parking',
        'pets_allowed', 'is_furnished', 'created_at'
    )
    search_fields = (
        'title', 'description', 'address', 'city', 
        'state', 'country', 'zipcode', 'title_deed_number',
        'parcel_number'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'display_map_link',
        'calculated_price_per_acre', 'calculated_price_per_sqft',
        'view_count', 'inquiry_count', 'favorite_count'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'description', 'property_type', 
                'listing_type', 'status'
            )
        }),
        ('Pricing', {
            'fields': (
                'price', 'currency', 'price_negotiable',
                'price_per_acre', 'price_per_sqft',
                'calculated_price_per_acre', 'calculated_price_per_sqft'
            )
        }),
        ('Building Details', {
            'fields': (
                'bedrooms', 'bathrooms', 'area_sqft',
                'floor_number', 'total_floors', 'year_built'
            ),
            'classes': ('collapse',)
        }),
        ('Land Size & Dimensions', {
            'fields': (
                'land_size_acres', 'land_size_sqft', 'land_size_sqm',
                'frontage_feet', 'depth_feet'
            ),
            'classes': ('collapse',)
        }),
        ('Land Characteristics', {
            'fields': (
                'is_corner_lot', 'is_waterfront', 'has_water_access',
                'has_electricity', 'has_road_access', 'has_sewer',
                'has_water_connection', 'has_gas_connection'
            ),
            'classes': ('collapse',)
        }),
        ('Zoning & Land Use', {
            'fields': (
                'zoning_type', 'zoning_description', 'permitted_uses',
                'is_subdivided', 'subdivision_potential', 'min_lot_size'
            ),
            'classes': ('collapse',)
        }),
        ('Physical Features', {
            'fields': (
                'topography', 'soil_type', 'elevation_feet',
                'slope_percentage', 'has_trees', 'is_cleared', 'is_fenced'
            ),
            'classes': ('collapse',)
        }),
        ('Environmental & Agricultural', {
            'fields': (
                'flood_zone', 'is_in_flood_zone', 'wetlands_present',
                'environmental_restrictions', 'water_source',
                'mineral_rights_included', 'is_irrigated',
                'irrigation_type', 'crop_history',
                'farming_equipment_included', 'has_barn',
                'has_greenhouse', 'has_storage_facilities'
            ),
            'classes': ('collapse',)
        }),
        ('Access & Infrastructure', {
            'fields': (
                'road_type', 'distance_to_main_road_miles',
                'has_easement', 'easement_details'
            ),
            'classes': ('collapse',)
        }),
        ('Development Potential', {
            'fields': (
                'development_ready', 'building_permits_approved',
                'max_building_coverage_percentage', 'floor_area_ratio',
                'max_building_height_feet'
            ),
            'classes': ('collapse',)
        }),
        ('Features & Amenities', {
            'fields': (
                'has_parking', 'parking_spaces', 'has_balcony',
                'has_elevator', 'has_swimming_pool', 'has_garden',
                'has_gym', 'has_security', 'is_furnished',
                'pets_allowed', 'has_air_conditioning', 'has_heating'
            ),
            'classes': ('collapse',)
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'state', 'country', 'zipcode',
                'latitude', 'longitude', 'formatted_address',
                'place_id', 'neighborhood', 'display_map_link'
            )
        }),
        ('Ownership & Management', {
            'fields': ('owner', 'agent')
        }),
        ('Legal & Documentation', {
            'fields': (
                'title_deed_number', 'parcel_number',
                'survey_available', 'last_surveyed_date'
            ),
            'classes': ('collapse',)
        }),
        ('Tax Information', {
            'fields': ('annual_property_tax', 'tax_assessment_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps & Availability', {
            'fields': (
                'created_at', 'updated_at', 'available_from',
                'listing_expiry_date'
            )
        }),
        ('Statistics', {
            'fields': ('view_count', 'inquiry_count', 'favorite_count'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [PropertyImageInline, PropertyDocumentInline, PricingHistoryInline]
    
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_available', 'mark_as_sold', 'mark_as_rented']
    
    def display_price(self, obj):
        return f"{obj.currency} {obj.price:,.2f}"
    display_price.short_description = 'Price'
    display_price.admin_order_field = 'price'
    
    def display_map_link(self, obj):
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html(
                '<a href="{}" target="_blank">View on Google Maps</a>',
                url
            )
        return "No coordinates"
    display_map_link.short_description = 'Map Location'
    
    def view_count(self, obj):
        return obj.views.count()
    view_count.short_description = 'Views'
    
    def inquiry_count(self, obj):
        return obj.inquiries.count()
    inquiry_count.short_description = 'Inquiries'
    
    def favorite_count(self, obj):
        return obj.favorited_by.count()
    favorite_count.short_description = 'Favorites'
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} properties marked as available.')
    mark_as_available.short_description = 'Mark selected as Available'
    
    def mark_as_sold(self, request, queryset):
        updated = queryset.update(status='sold')
        self.message_user(request, f'{updated} properties marked as sold.')
    mark_as_sold.short_description = 'Mark selected as Sold'
    
    def mark_as_rented(self, request, queryset):
        updated = queryset.update(status='rented')
        self.message_user(request, f'{updated} properties marked as rented.')
    mark_as_rented.short_description = 'Mark selected as Rented'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image_type', 'caption', 'is_primary', 'uploaded_at', 'image_preview')
    list_filter = ('image_type', 'is_primary', 'uploaded_at')
    search_fields = ('property__title', 'caption')
    readonly_fields = ('uploaded_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'property', 'document_type', 'title', 
        'is_public', 'uploaded_by', 'uploaded_at'
    )
    list_filter = ('document_type', 'is_public', 'uploaded_at')
    search_fields = ('property__title', 'title', 'description')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        (None, {
            'fields': ('property', 'document_type', 'title', 'description')
        }),
        ('Document', {
            'fields': ('document', 'is_public')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at')
        })
    )


@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'viewer_ip', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('property__title', 'user__username', 'viewer_ip')
    readonly_fields = ('viewed_at',)
    date_hierarchy = 'viewed_at'


@admin.register(PricingHistory)
class PricingHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'property', 'old_price', 'new_price', 
        'price_change', 'percentage_change', 
        'changed_by', 'changed_at'
    )
    list_filter = ('changed_at',)
    search_fields = ('property__title', 'reason')
    readonly_fields = ('changed_at', 'price_change', 'percentage_change')
    date_hierarchy = 'changed_at'
    
    def price_change(self, obj):
        change = obj.new_price - obj.old_price
        color = 'green' if change >= 0 else 'red'
        return format_html(
            '<span style="color: {};">{:+,.2f}</span>',
            color, change
        )
    price_change.short_description = 'Change'
    
    def percentage_change(self, obj):
        if obj.old_price > 0:
            pct = ((obj.new_price - obj.old_price) / obj.old_price) * 100
            color = 'green' if pct >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:+.2f}%</span>',
                color, pct
            )
        return "N/A"
    percentage_change.short_description = '% Change'


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        'property', 'inquirer_name', 'inquirer_email',
        'status', 'created_at', 'responded_at'
    )
    list_filter = ('status', 'created_at', 'responded_at')
    search_fields = (
        'property__title', 'inquirer_name', 
        'inquirer_email', 'inquirer_phone', 'message'
    )
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Property', {
            'fields': ('property',)
        }),
        ('Inquirer Information', {
            'fields': (
                'inquirer_name', 'inquirer_email', 
                'inquirer_phone', 'user'
            )
        }),
        ('Inquiry Details', {
            'fields': ('message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'responded_at')
        })
    )
    
    actions = ['mark_as_contacted', 'mark_as_scheduled']
    
    def mark_as_contacted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='contacted', responded_at=timezone.now())
        self.message_user(request, f'{updated} inquiries marked as contacted.')
    mark_as_contacted.short_description = 'Mark as Contacted'
    
    def mark_as_scheduled(self, request, queryset):
        updated = queryset.update(status='scheduled')
        self.message_user(request, f'{updated} inquiries marked as visit scheduled.')
    mark_as_scheduled.short_description = 'Mark as Visit Scheduled'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'property__title', 'notes')
    readonly_fields = ('added_at',)
    date_hierarchy = 'added_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'property')
        }),
        ('Additional Info', {
            'fields': ('notes', 'added_at')
        })
    )