from django.urls import path
from . import views

urlpatterns = [
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('create/<int:property_pk>/', views.create_booking, name='create_booking'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
]