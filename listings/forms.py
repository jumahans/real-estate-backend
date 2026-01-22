from django import forms
from .models import Property, PropertyImage, Inquiry

class PropertyCreateForm(forms.ModelForm):
    """Form for the Agent to add/edit properties"""
    class Meta:
        model = Property
        exclude = ['owner', 'created_at', 'updated_at', 'latitude', 'longitude']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Luxury Villa in Suburbs'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'KES'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'area_sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'year_built': forms.NumberInput(attrs={'class': 'form-control'}),
            'land_size_acres': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Checkboxes
            'price_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_swimming_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_garden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PropertyImageForm(forms.ModelForm):
    """Form for uploading images (usually used in a FormSet)"""
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Living Room'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PropertySearchForm(forms.Form):
    """Filter form for the listing page"""
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search by city, title...'
    }))
    property_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Property.PROPERTY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'}))

class InquiryForm(forms.ModelForm):
    """Simple contact form for potential buyers"""
    class Meta:
        model = Inquiry
        fields = ['inquirer_name', 'inquirer_email', 'inquirer_phone', 'message']
        widgets = {
            'inquirer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'inquirer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'inquirer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254...'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'I am interested in this property...'}),
        }