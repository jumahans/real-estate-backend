from django.contrib import admin
from .models import Agent, Profile, Property, Booking

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'user']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'max_viewers', 'is_active']
    list_filter = ['type', 'is_active']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'start_datetime', 'status', 'version']
    list_filter = ['status', 'property__type', 'start_datetime']
    search_fields = ['user__username', 'property__title']
    actions = ['confirm_bookings', 'cancel_bookings']

    def confirm_bookings(self, request, queryset):
        # Triggers your model's save() logic (inactivation)
        for booking in queryset:
            booking.status = 'confirmed'
            booking.save()
    confirm_bookings.short_description = "Confirm selected bookings"

    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
    cancel_bookings.short_description = "Cancel selected bookings"
