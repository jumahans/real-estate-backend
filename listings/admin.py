from django.contrib import admin
from django.utils.html import format_html
from core.admin import admin_site  # Import our custom analytical admin
from .models import Property, PropertyImage, Inquiry, Favorite
from django.http import JsonResponse
from django.urls import path
from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto; border-radius: 5px;" />', obj.image.url)
        return ""

@admin.register(Property, site=admin_site)
class PropertyAdmin(admin.ModelAdmin):
    change_list_template = 'admin/listings/property_analytics.html'
    list_display = ('title_display', 'price_display', 'property_type', 'status_badge', 'city', 'created_at')
    list_filter = ('status', 'property_type', 'city', 'created_at')
    search_fields = ('title', 'address', 'city', 'description')
    inlines = [PropertyImageInline]
    list_per_page = 20
    
    # Custom display methods for a "Luxury" feel in the admin list
    def title_display(self, obj):
        return format_html('<b>{}</b>', obj.title)
    title_display.short_description = "Property Title"

    def price_display(self, obj):
        return f"{obj.currency} {obj.price:,.0f}"
    price_display.short_description = "Price"

    def status_badge(self, obj):
        colors = {
            'available': '#28a745', # Green
            'sold': '#dc3545',      # Red
            'rented': '#ffc107',    # Yellow
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 50px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = "Status"

    def get_urls(self):
        urls = super().get_urls()
        return [path('analytics/', self.analytics_api, name='analytics')] + urls
    
    def analytics_api(self, request):
        now = datetime.now()
        labels, data = [], []
        
        # Last 12 months
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
            'labels': labels[::-1],  # Reverse (oldest first)
            'data': data[::-1],
            'total_sold': total_sold,
            'total_revenue': float(revenue),
            'sell_rate': sell_rate,
            'available': Property.objects.filter(status='available').count()
        })

@admin.register(Inquiry, site=admin_site)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('inquirer_name', 'property_link', 'inquirer_email', 'created_at_formatted')
    list_filter = ('created_at',)
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