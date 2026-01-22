from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import LogEntry
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncMonth
from django.utils.html import format_html
from django.urls import reverse
import json

from .models import Profile

class ArthiAdminSite(admin.AdminSite):
    """
    High-Performance Analytical Admin Dashboard for ArthiProperties.
    Centralizes all business intelligence and management.
    """
    site_header = "ArthiProperties HQ"
    index_title = "Executive Command Center"
    site_title = "ArthiProperties Admin"
    enable_nav_sidebar = True

    def index(self, request, extra_context=None):
        # Lazy imports to prevent circular dependencies
        from listings.models import Property, Inquiry
        from booking.models import Booking

        # =================================================
        # 1. CORE KPI CARDS
        # =================================================
        total_properties = Property.objects.count()
        active_listings = Property.objects.filter(status='available').count()
        total_users = User.objects.count()
        total_inquiries = Inquiry.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        
        # Portfolio Calculation (Handle None if DB is empty)
        portfolio_agg = Property.objects.filter(status='available').aggregate(total=Sum('price'))
        portfolio_value = portfolio_agg['total'] or 0

        # =================================================
        # 2. CHARTS & ANALYTICS
        # =================================================
        
        # --- A. Inventory Breakdown (Pie Chart) ---
        prop_types = Property.objects.values('property_type').annotate(count=Count('id')).order_by('-count')
        pie_labels = [p['property_type'].replace('_', ' ').title() for p in prop_types]
        pie_data = [p['count'] for p in prop_types]

        # --- B. Lead Generation Velocity (Line Chart) ---
        # Group inquiries by month
        inquiries_trend = Inquiry.objects.annotate(month=TruncMonth('created_at'))\
            .values('month').annotate(count=Count('id')).order_by('month')
        
        line_labels = [i['month'].strftime('%b %Y') for i in inquiries_trend]
        line_data = [i['count'] for i in inquiries_trend]

        # --- C. Geographic Hotspots (Bar Chart) ---
        # Top 5 Cities by property count
        city_stats = Property.objects.values('city').annotate(count=Count('id')).order_by('-count')[:5]
        bar_labels = [c['city'] for c in city_stats]
        bar_data = [c['count'] for c in city_stats]

        # =================================================
        # 3. RECENT ACTIVITY FEED
        # =================================================
        # Fetch the last 10 actions performed in the admin (Audit Log)
        recent_actions = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:6]

        # =================================================
        # 4. CONTEXT ASSEMBLY
        # =================================================
        extra_context = extra_context or {}
        extra_context.update({
            # KPIs
            'kpi': {
                'properties': total_properties,
                'active': active_listings,
                'users': total_users,
                'inquiries': total_inquiries,
                'bookings': pending_bookings,
                'value': portfolio_value,
            },
            # Charts JSON
            'charts': {
                'pie_labels': json.dumps(pie_labels),
                'pie_data': json.dumps(pie_data),
                'line_labels': json.dumps(line_labels),
                'line_data': json.dumps(line_data),
                'bar_labels': json.dumps(bar_labels),
                'bar_data': json.dumps(bar_data),
            },
            # Activity Log
            'recent_actions': recent_actions,
        })
        return super().index(request, extra_context)

# ---------------------------------------------------------
# INSTANTIATE CUSTOM SITE
# ---------------------------------------------------------
admin_site = ArthiAdminSite(name='arthi_admin')


# ---------------------------------------------------------
# CUSTOM MODEL ADMINS
# ---------------------------------------------------------

@admin.register(Profile, site=admin_site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'phone', 'role_badge', 'date_joined')
    list_filter = ('is_agent', 'user__date_joined')
    search_fields = ('user__username', 'user__email', 'phone')
    ordering = ('-user__date_joined',)
    actions = ['make_agent', 'remove_agent']

    def user_info(self, obj):
        return format_html(
            '<div><span style="font-weight:bold; font-size:1.1em;">{}</span><br>'
            '<span style="color:#666;">{}</span></div>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = "User Details"

    def role_badge(self, obj):
        if obj.is_agent:
            return format_html('<span style="background:#1B4D3E; color:white; padding:4px 8px; border-radius:4px;">Agent</span>')
        return format_html('<span style="background:#6c757d; color:white; padding:4px 8px; border-radius:4px;">Customer</span>')
    role_badge.short_description = "Role"

    def date_joined(self, obj):
        return obj.user.date_joined.strftime("%b %d, %Y")
    date_joined.admin_order_field = 'user__date_joined'

    # Bulk Actions
    def make_agent(self, request, queryset):
        queryset.update(is_agent=True)
    make_agent.short_description = "Promote selected users to Agents"

    def remove_agent(self, request, queryset):
        queryset.update(is_agent=False)
    remove_agent.short_description = "Demote selected users to Customers"

# ---------------------------------------------------------
# SYSTEM MODELS REGISTRATION
# ---------------------------------------------------------

# Re-register Standard User Model with enhanced features if needed, 
# or just standard registration to the new site.
admin_site.register(User, UserAdmin)
admin_site.register(Group)

# Register Audit Log (Optional: View-only for security)
@admin.register(LogEntry, site=admin_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'action_flag', 'change_message')
    readonly_fields = ('content_type', 'user', 'action_time', 'object_id', 'object_repr', 'action_flag', 'change_message')
    
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False