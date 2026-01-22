from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_site  # Import the custom admin

urlpatterns = [
    path('admin/', admin_site.urls), # Use custom admin_site
    path('', include('listings.urls')),
    path('auth/', include('core.urls')), 
    path('booking/', include('booking.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)