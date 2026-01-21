from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from .models import (
    Property, PropertyImage, PropertyDocument, Inquiry, Favorite
)


class PropertyCreateForm(forms.ModelForm):
    """Form for creating a new property listing"""
    
    class Meta:
        model = Property
        fields = [
            # Basic Information
            'title', 'description', 'property_type', 'listing_type', 'status',
            
            # Pricing
            'price', 'currency', 'price_negotiable',
            
            # Property Details (Buildings)
            'bedrooms', 'bathrooms', 'area_sqft', 'floor_number', 
            'total_floors', 'year_built',
            
            # Land Size & Dimensions
            'land_size_acres', 'land_size_sqft', 'land_size_sqm',
            'frontage_feet', 'depth_feet',
            
            # Land Characteristics
            'is_corner_lot', 'is_waterfront', 'has_water_access',
            'has_electricity', 'has_road_access', 'has_sewer',
            'has_water_connection', 'has_gas_connection',
            
            # Zoning & Land Use
            'zoning_type', 'zoning_description', 'permitted_uses',
            'is_subdivided', 'subdivision_potential', 'min_lot_size',
            
            # Land Physical Features
            'topography', 'soil_type', 'elevation_feet', 'slope_percentage',
            'has_trees', 'is_cleared', 'is_fenced',
            
            # Environmental & Agricultural
            'flood_zone', 'is_in_flood_zone', 'wetlands_present',
            'environmental_restrictions', 'water_source', 'mineral_rights_included',
            
            # Agricultural Land Specifics
            'is_irrigated', 'irrigation_type', 'crop_history',
            'farming_equipment_included', 'has_barn', 'has_greenhouse',
            'has_storage_facilities',
            
            # Access & Infrastructure
            'road_type', 'distance_to_main_road_miles', 'has_easement',
            'easement_details',
            
            # Development Potential
            'development_ready', 'building_permits_approved',
            'max_building_coverage_percentage', 'floor_area_ratio',
            'max_building_height_feet',
            
            # Features & Amenities
            'has_parking', 'parking_spaces', 'has_balcony', 'has_elevator',
            'has_swimming_pool', 'has_garden', 'has_gym', 'has_security',
            'is_furnished', 'pets_allowed', 'has_air_conditioning', 'has_heating',
            
            # Location
            'address', 'city', 'state', 'country', 'zipcode',
            'latitude', 'longitude', 'formatted_address', 'place_id', 'neighborhood',
            
            # Legal & Documentation
            'title_deed_number', 'parcel_number', 'survey_available',
            'last_surveyed_date',
            
            # Tax Information
            'annual_property_tax', 'tax_assessment_value',
            
            # Dates
            'available_from', 'listing_expiry_date',
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the property'
            }),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'listing_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '3'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
            'area_sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'land_size_acres': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0'
            }),
            'land_size_sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'land_size_sqm': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'frontage_feet': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'depth_feet': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'zoning_type': forms.Select(attrs={'class': 'form-control'}),
            'zoning_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'permitted_uses': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'topography': forms.Select(attrs={'class': 'form-control'}),
            'soil_type': forms.Select(attrs={'class': 'form-control'}),
            'elevation_feet': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'slope_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'flood_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'environmental_restrictions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'water_source': forms.TextInput(attrs={'class': 'form-control'}),
            'irrigation_type': forms.TextInput(attrs={'class': 'form-control'}),
            'crop_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'road_type': forms.TextInput(attrs={'class': 'form-control'}),
            'distance_to_main_road_miles': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'easement_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'max_building_coverage_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'floor_area_ratio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'max_building_height_feet': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'parking_spaces': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP/Postal Code'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'formatted_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'place_id': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'title_deed_number': forms.TextInput(attrs={'class': 'form-control'}),
            'parcel_number': forms.TextInput(attrs={'class': 'form-control'}),
            'last_surveyed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'annual_property_tax': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'tax_assessment_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'listing_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'year_built': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1800',
                'max': '2100'
            }),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_lot_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }
        
        help_texts = {
            'land_size_acres': 'Total land area in acres',
            'land_size_sqft': 'Auto-calculated if acres provided',
            'price_negotiable': 'Check if price is negotiable',
            'latitude': 'Use Google Maps to find coordinates',
            'longitude': 'Use Google Maps to find coordinates',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        property_type = cleaned_data.get('property_type')
        
        # Validate that land properties have land size
        if property_type and 'land' in property_type:
            if not cleaned_data.get('land_size_acres') and not cleaned_data.get('land_size_sqft'):
                raise forms.ValidationError(
                    "Land properties must have land size specified (in acres or square feet)."
                )
        
        # Validate building properties have area
        if property_type and 'land' not in property_type:
            if not cleaned_data.get('area_sqft'):
                raise forms.ValidationError(
                    "Building properties must have area specified in square feet."
                )
        
        return cleaned_data


class PropertyUpdateForm(PropertyCreateForm):
    """Form for updating existing property - inherits from create form"""
    
    class Meta(PropertyCreateForm.Meta):
        pass


class PropertySearchForm(forms.Form):
    """Advanced search form for properties"""
    
    # Basic filters
    property_type = forms.ChoiceField(
        choices=[('', 'Any Type')] + Property.PROPERTY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    listing_type = forms.ChoiceField(
        choices=[('', 'Any')] + Property.LISTING_TYPE,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Location filters
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    
    # Price filters
    min_price = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )
    
    # Building filters
    min_bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Bedrooms'
        })
    )
    
    max_bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Bedrooms'
        })
    )
    
    min_bathrooms = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Bathrooms',
            'step': '0.5'
        })
    )
    
    # Land filters
    min_land_acres = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Acres',
            'step': '0.01'
        })
    )
    
    max_land_acres = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Acres',
            'step': '0.01'
        })
    )
    
    zoning_type = forms.ChoiceField(
        choices=[('', 'Any Zoning')] + Property.ZONING_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    topography = forms.ChoiceField(
        choices=[('', 'Any Topography')] + Property.TOPOGRAPHY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Boolean filters
    is_waterfront = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_electricity = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_water_access = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    subdivision_potential = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_parking = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_swimming_pool = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter location (city, address, neighborhood)',
            'id': 'location-search'
        })
    )
    
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    radius_miles = forms.DecimalField(
        required=False,
        initial=10,
        min_value=Decimal('0.1'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Radius (miles)',
            'step': '0.1'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate price range
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(
                "Minimum price cannot be greater than maximum price."
            )
        
        # Validate bedroom range
        min_bedrooms = cleaned_data.get('min_bedrooms')
        max_bedrooms = cleaned_data.get('max_bedrooms')
        
        if min_bedrooms and max_bedrooms and min_bedrooms > max_bedrooms:
            raise forms.ValidationError(
                "Minimum bedrooms cannot be greater than maximum bedrooms."
            )
        
        # Validate land size range
        min_land = cleaned_data.get('min_land_acres')
        max_land = cleaned_data.get('max_land_acres')
        
        if min_land and max_land and min_land > max_land:
            raise forms.ValidationError(
                "Minimum land size cannot be greater than maximum land size."
            )
        
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    """Form for uploading property images"""
    
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary', 'image_type']
        
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional caption for this image'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image_type': forms.Select(attrs={'class': 'form-control'}),
        }
        
        help_texts = {
            'is_primary': 'Set this as the main property image',
            'image_type': 'Select the type of image being uploaded',
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # Validate file size (e.g., max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file size cannot exceed 5MB."
                )
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(valid_extensions)}"
                )
        
        return image


class PropertyDocumentForm(forms.ModelForm):
    """Form for uploading property documents"""
    
    class Meta:
        model = PropertyDocument
        fields = ['document_type', 'document', 'title', 'description', 'is_public']
        
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        help_texts = {
            'is_public': 'Make this document publicly accessible',
            'document': 'Accepted formats: PDF, DOC, DOCX, XLS, XLSX',
        }
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        
        if document:
            # Validate file size (e.g., max 10MB)
            if document.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "Document file size cannot exceed 10MB."
                )
            
            # Validate file type
            valid_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx']
            ext = document.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f"Invalid file type. Allowed types: {', '.join(valid_extensions)}"
                )
        
        return document


class InquiryForm(forms.ModelForm):
    """Form for submitting property inquiries"""
    
    class Meta:
        model = Inquiry
        fields = ['inquirer_name', 'inquirer_email', 'inquirer_phone', 'message']
        
        widgets = {
            'inquirer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'inquirer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address',
                'required': True
            }),
            'inquirer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number (optional)'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your message or questions about this property',
                'required': True
            }),
        }
        
        labels = {
            'inquirer_name': 'Full Name',
            'inquirer_email': 'Email Address',
            'inquirer_phone': 'Phone Number',
            'message': 'Your Message',
        }
    
    def clean_inquirer_email(self):
        email = self.cleaned_data.get('inquirer_email')
        
        # Add any custom email validation here
        if email:
            email = email.lower().strip()
        
        return email
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        
        # Ensure message has minimum length
        if message and len(message.strip()) < 10:
            raise forms.ValidationError(
                "Message must be at least 10 characters long."
            )
        
        return message