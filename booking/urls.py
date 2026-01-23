from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # Will create views.py next

router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet)
router.register(r'bookings', views.BookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
