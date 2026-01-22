# urls.py (in your properties app)

from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #  PROPERTY LISTING URLS 
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('search/', views.property_search, name='property_search'),
    
    #  MAP SEARCH URLS 
    path('map-search/', views.property_map_search, name='property_map_search'),
    path('nearby/', views.property_nearby_search, name='property_nearby_search'),
    

    #  INQUIRY URLS 
    path('<int:property_pk>/inquiry/', views.property_inquiry_create, name='property_inquiry'),
    path('inquiries/', views.inquiry_list, name='inquiry_list'),
    path('inquiry/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    
    #  FAVORITE URLS 
    path('<int:property_pk>/favorite/toggle/', views.property_favorite_toggle, name='property_favorite_toggle'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    
    #  PROPERTY MANAGEMENT URLS 
    path('dashboard/', views.property_dashboard, name='property_dashboard'),
    path('<int:pk>/analytics/', views.property_analytics, name='property_analytics'),
    
    #  FEATURED & SPECIAL URLS 
    path('featured/', views.property_featured, name='property_featured'),
    path('latest/', views.property_latest, name='property_latest'),
    path('type/<str:property_type>/', views.property_by_type, name='property_by_type'),
    path('city/<str:city>/', views.property_by_city, name='property_by_city'),
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)