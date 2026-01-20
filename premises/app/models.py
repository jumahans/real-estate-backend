from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone


class Property(models.Model):
    """Model for all real estate properties with enhanced land support"""
    
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('condo', 'Condo'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
        ('duplex', 'Duplex'),
        ('bungalow', 'Bungalow'),
        ('mansion', 'Mansion'),
        ('residential_land', 'Residential Land'),
        ('commercial_land', 'Commercial Land'),
        ('agricultural_land', 'Agricultural Land'),
        ('industrial_land', 'Industrial Land'),
        ('mixed_use_land', 'Mixed Use Land'),
        ('vacant_land', 'Vacant Land'),
        ('office', 'Office Space'),
        ('retail', 'Retail Space'),
        ('warehouse', 'Warehouse'),
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
        ('shopping_mall', 'Shopping Mall'),
        ('business_park', 'Business Park'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('sold', 'Sold'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('pending', 'Pending'),
    ]
    
    LISTING_TYPE = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('lease', 'For Lease'),
    ]
    
    ZONING_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('agricultural', 'Agricultural'),
        ('mixed_use', 'Mixed Use'),
        ('recreational', 'Recreational'),
        ('institutional', 'Institutional'),
        ('conservation', 'Conservation'),
        ('unzoned', 'Unzoned'),
    ]
    
    SOIL_TYPES = [
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loam', 'Loam'),
        ('silt', 'Silt'),
        ('peat', 'Peat'),
        ('chalky', 'Chalky'),
        ('rocky', 'Rocky'),
        ('mixed', 'Mixed'),
    ]
    
    TOPOGRAPHY_TYPES = [
        ('flat', 'Flat'),
        ('sloped', 'Sloped'),
        ('hilly', 'Hilly'),
        ('mountainous', 'Mountainous'),
        ('valley', 'Valley'),
        ('plateau', 'Plateau'),
        ('undulating', 'Undulating'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE, default='sale')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Pricing
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')
    price_negotiable = models.BooleanField(default=False)
    price_per_acre = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Calculated price per acre for land"
    )
    price_per_sqft = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Price per square foot"
    )
    
    # Property Details (for buildings)
    bedrooms = models.IntegerField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    bathrooms = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(Decimal('0.5'))]
    )
    area_sqft = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Building area in square feet",
        blank=True,
        null=True
    )
    floor_number = models.IntegerField(blank=True, null=True)
    total_floors = models.IntegerField(blank=True, null=True)
    year_built = models.IntegerField(
        blank=True, 
        null=True,
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(2100)
        ]
    )
    
    # ===== ENHANCED LAND-SPECIFIC FIELDS =====
    
    # Land Size & Dimensions
    land_size_acres = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Total land size in acres"
    )
    land_size_sqft = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total land size in square feet"
    )
    land_size_sqm = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total land size in square meters"
    )
    frontage_feet = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Street frontage in feet"
    )
    depth_feet = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Lot depth in feet"
    )
    
    # Land Characteristics
    is_corner_lot = models.BooleanField(default=False)
    is_waterfront = models.BooleanField(default=False)
    has_water_access = models.BooleanField(default=False)
    has_electricity = models.BooleanField(default=False)
    has_road_access = models.BooleanField(default=False)
    has_sewer = models.BooleanField(default=False)
    has_water_connection = models.BooleanField(default=False)
    has_gas_connection = models.BooleanField(default=False)
    
    # Zoning & Land Use
    zoning_type = models.CharField(
        max_length=100, 
        choices=ZONING_TYPES,
        blank=True, 
        null=True
    )
    zoning_description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed zoning information"
    )
    permitted_uses = models.TextField(
        blank=True,
        null=True,
        help_text="List of permitted land uses"
    )
    is_subdivided = models.BooleanField(default=False)
    subdivision_potential = models.BooleanField(
        default=False,
        help_text="Can the land be subdivided?"
    )
    min_lot_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Minimum lot size per subdivision regulations"
    )
    
    # Land Physical Features
    topography = models.CharField(
        max_length=50,
        choices=TOPOGRAPHY_TYPES,
        blank=True,
        null=True
    )
    soil_type = models.CharField(
        max_length=50,
        choices=SOIL_TYPES,
        blank=True,
        null=True
    )
    elevation_feet = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Elevation above sea level in feet"
    )
    slope_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    has_trees = models.BooleanField(default=False)
    is_cleared = models.BooleanField(default=False)
    is_fenced = models.BooleanField(default=False)
    
    # Environmental & Agricultural
    flood_zone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="FEMA flood zone designation"
    )
    is_in_flood_zone = models.BooleanField(default=False)
    wetlands_present = models.BooleanField(default=False)
    environmental_restrictions = models.TextField(
        blank=True,
        null=True
    )
    water_source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Well, municipal, river, etc."
    )
    mineral_rights_included = models.BooleanField(default=True)
    
    # Agricultural Land Specifics
    is_irrigated = models.BooleanField(default=False)
    irrigation_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Drip, sprinkler, flood, etc."
    )
    crop_history = models.TextField(
        blank=True,
        null=True,
        help_text="Previous crops grown on land"
    )
    farming_equipment_included = models.BooleanField(default=False)
    has_barn = models.BooleanField(default=False)
    has_greenhouse = models.BooleanField(default=False)
    has_storage_facilities = models.BooleanField(default=False)
    
    # Access & Infrastructure
    road_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Paved, gravel, dirt, private, etc."
    )
    distance_to_main_road_miles = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )
    has_easement = models.BooleanField(default=False)
    easement_details = models.TextField(blank=True, null=True)
    
    # Development Potential
    development_ready = models.BooleanField(default=False)
    building_permits_approved = models.BooleanField(default=False)
    max_building_coverage_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Maximum percentage of lot that can be built on"
    )
    floor_area_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Ratio of total building floor area to lot size"
    )
    max_building_height_feet = models.IntegerField(
        blank=True,
        null=True
    )
    
    # Features & Amenities (for developed properties)
    has_parking = models.BooleanField(default=False)
    parking_spaces = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)]
    )
    has_balcony = models.BooleanField(default=False)
    has_elevator = models.BooleanField(default=False)
    has_swimming_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_security = models.BooleanField(default=False)
    is_furnished = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=False)
    has_heating = models.BooleanField(default=False)
    
    # Location (Google Maps Integration)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, db_index=True)
    zipcode = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    formatted_address = models.TextField()
    place_id = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    
    # Ownership & Management
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_properties'
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_properties'
    )
    
    # Legal & Documentation
    title_deed_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    parcel_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Tax parcel/lot number"
    )
    survey_available = models.BooleanField(default=False)
    last_surveyed_date = models.DateField(blank=True, null=True)
    
    # Tax Information
    annual_property_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    tax_assessment_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_from = models.DateField(blank=True, null=True)
    listing_expiry_date = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['property_type']),
            models.Index(fields=['listing_type']),
            models.Index(fields=['country', 'city']),
            models.Index(fields=['price']),
            models.Index(fields=['land_size_acres']),
            models.Index(fields=['zoning_type']),
            models.Index(fields=['is_waterfront']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.city}, {self.country}"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def is_land(self):
        return 'land' in self.property_type
    
    @property
    def full_location(self):
        return self.formatted_address
    
    @property
    def calculated_price_per_acre(self):
        """Calculate price per acre if land size is available"""
        if self.land_size_acres and self.land_size_acres > 0:
            return self.price / self.land_size_acres
        return None
    
    @property
    def calculated_price_per_sqft(self):
        """Calculate price per square foot"""
        total_sqft = self.land_size_sqft or self.area_sqft
        if total_sqft and total_sqft > 0:
            return self.price / total_sqft
        return None
    
    def save(self, *args, **kwargs):
        """Auto-calculate price per acre/sqft on save"""
        if self.is_land:
            self.price_per_acre = self.calculated_price_per_acre
        if self.land_size_sqft or self.area_sqft:
            self.price_per_sqft = self.calculated_price_per_sqft
        super().save(*args, **kwargs)


class PropertyImage(models.Model):
    """Model for storing multiple images per property"""
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='properties/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    image_type = models.CharField(
        max_length=50,
        choices=[
            ('exterior', 'Exterior'),
            ('interior', 'Interior'),
            ('aerial', 'Aerial View'),
            ('land', 'Land View'),
            ('boundary', 'Boundary'),
            ('infrastructure', 'Infrastructure'),
            ('surrounding', 'Surrounding Area'),
            ('document', 'Document/Map'),
        ],
        default='exterior'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyDocument(models.Model):
    """Model for storing property documents (surveys, deeds, permits)"""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('title_deed', 'Title Deed'),
            ('survey', 'Survey Report'),
            ('zoning', 'Zoning Document'),
            ('permit', 'Building Permit'),
            ('tax', 'Tax Document'),
            ('environmental', 'Environmental Report'),
            ('soil_test', 'Soil Test Report'),
            ('appraisal', 'Appraisal Report'),
            ('other', 'Other'),
        ]
    )
    document = models.FileField(upload_to='property_documents/%Y/%m/%d/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this document is publicly accessible"
    )
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.document_type} - {self.property.title}"


class PropertyView(models.Model):
    """Model to track property views for analytics"""
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='views'
    )
    viewer_ip = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['property', '-viewed_at']),
        ]
    
    def __str__(self):
        return f"View of {self.property.title} at {self.viewed_at}"


class PricingHistory(models.Model):
    """Model to track price changes for analytics"""
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='price_history'
    )
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Pricing Histories"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['property', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.property.title}: {self.old_price} → {self.new_price}"
    
    # @property
    # def price_change(self):
    #     return self.new_price - self.old_price

    # @property
    # def percentage_change(self):
    #     if self.old_price > 0:
    #         return ((self.new_price - self.old_price) / self.old_price) * 100
    #     return 0.0



class Inquiry(models.Model):
    """Model for property inquiries from potential buyers/renters"""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    inquirer_name = models.CharField(max_length=200)
    inquirer_email = models.EmailField()
    inquirer_phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('scheduled', 'Visit Scheduled'),
            ('closed', 'Closed'),
        ],
        default='new'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Inquiries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry for {self.property.title} from {self.inquirer_name}"


class Favorite(models.Model):
    """Model for users to save favorite properties"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.property.title}"