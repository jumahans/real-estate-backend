from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.property_list, name='property_list'),
    path('search/', views.property_search, name='property_search'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('map/', views.property_map_search, name='property_map_search'),
    path('nearby/', views.property_nearby_search, name='property_nearby_search'),

    # User Personal
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/toggle/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('my-inquiries/', views.inquiry_list, name='inquiry_list'),
]