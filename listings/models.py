from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from core.models import TimeStampedModel

User = get_user_model()

class Property(TimeStampedModel):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'), ('house', 'House'), ('villa', 'Villa'),
        ('commercial', 'Commercial'), ('land', 'Land'), ('commercial_land', 'Commercial Land'),
        ('bungalow', 'Bungalow'), ('office', 'Office Space'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'), ('rented', 'Rented'),
        ('sold', 'Sold'), ('pending', 'Pending'),
    ]

    LISTING_TYPE = [
        ('sale', 'For Sale'), ('rent', 'For Rent'), ('lease', 'For Lease'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE, default='sale') # Fixed
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    price_negotiable = models.BooleanField(default=False)
    
    # Location
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kenya')
    zipcode = models.CharField(max_length=20, blank=True, null=True) # Fixed
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Details
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    year_built = models.IntegerField(blank=True, null=True)
    land_size_acres = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    zoning_type = models.CharField(max_length=100, blank=True, null=True) # Fixed
    
    # Amenities & Features (Booleans)
    has_parking = models.BooleanField(default=False)
    parking_spaces = models.IntegerField(default=0) # Fixed
    has_swimming_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_security = models.BooleanField(default=False)
    has_elevator = models.BooleanField(default=False) # Fixed
    has_gym = models.BooleanField(default=False) # Fixed
    has_air_conditioning = models.BooleanField(default=False) # Fixed
    has_road_access = models.BooleanField(default=False) # Fixed
    has_electricity = models.BooleanField(default=False) # Fixed
    has_water_connection = models.BooleanField(default=False) # Fixed
    is_waterfront = models.BooleanField(default=False) # Fixed

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_properties')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title} - {self.city}"

class PropertyImage(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    image_type = models.CharField(max_length=50, default='exterior')

class PropertyDocument(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='property_docs/')
    document_type = models.CharField(max_length=50, default='other')
    is_public = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class PropertyView(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    viewer_ip = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

class PricingHistory(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

class Inquiry(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    inquirer_name = models.CharField(max_length=200)
    inquirer_email = models.EmailField()
    inquirer_phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=20, default='new', choices=[('new', 'New'), ('read', 'Read')])

class Favorite(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'property')