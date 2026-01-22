from django.contrib import admin
from django.utils.html import format_html
from core.admin import admin_site  # Import custom admin
from .models import Booking, BookingSettings

@admin.register(Booking, site=admin_site)
class BookingAdmin(admin.ModelAdmin):
    # Use 'listing' if that's your model field name, otherwise 'property'
    list_display = ('user_info', 'property_info', 'date_display', 'status_badge')
    list_filter = ('status', 'start_datetime')
    search_fields = ('user__username', 'user__email', 'listing__title')
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']

    def user_info(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.username})"
    user_info.short_description = "Client"

    def property_info(self, obj):
        # Ensure this matches your model (obj.listing or obj.property)
        return obj.listing.title if hasattr(obj, 'listing') else obj.property.title
    property_info.short_description = "Property"

    def date_display(self, obj):
        return obj.start_datetime.strftime("%b %d, %H:%M")
    date_display.short_description = "Scheduled Time"

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',   # Yellow (Warning)
            'confirmed': '#17a2b8', # Teal (Info)
            'completed': '#28a745', # Green (Success)
            'cancelled': '#dc3545', # Red (Danger)
        }
        color = colors.get(obj.status, 'grey')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 50px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = "Status"

    # Admin Actions
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Confirm selected bookings"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected bookings as completed"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Cancel selected bookings"

@admin.register(BookingSettings, site=admin_site)
class BookingSettingsAdmin(admin.ModelAdmin):
    # FIXED: Changed 'property' to 'listing' (or whatever your OneToOne field is named)
    # If your model uses 'property', change it back. If it uses 'listing', keep this.
    list_display = ('get_property_title', 'slot_duration_minutes', 'is_active')
    search_fields = ('listing__title',) 
    list_filter = ('is_active',)

    def get_property_title(self, obj):
        # Handle both naming conventions safely
        return obj.listing.title if hasattr(obj, 'listing') else obj.property.title
    get_property_title.short_description = 'Property'

    def slot_duration_minutes(self, obj):
        # Assuming your model might call it 'slot_duration' or 'duration'
        return f"{obj.slot_duration} mins"
    slot_duration_minutes.short_description = 'Duration'