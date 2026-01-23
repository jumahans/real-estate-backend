import os
import django
import random
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.core.files.base import ContentFile

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'premises.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Profile
from listings.models import Property, PropertyImage, Inquiry, Favorite
from booking.models import BookingSettings, Booking

User = get_user_model()

def run_seed():
    print("🌱 Seeding Database...")

    # 1. Create Users
    print("Creating Users...")
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@arthi.com', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('admin123')
    admin_user.save()

    agent_user, _ = User.objects.get_or_create(
        username='agent_jane',
        defaults={'email': 'jane@arthi.com', 'first_name': 'Jane', 'last_name': 'Doe'}
    )
    agent_user.set_password('password123')
    agent_user.save()
    # Update Agent Profile
    if hasattr(agent_user, 'profile'):
        agent_user.profile.is_agent = True
        agent_user.profile.phone = "+254700000001"
        agent_user.profile.save()

    client_user, _ = User.objects.get_or_create(
        username='client_john',
        defaults={'email': 'john@client.com', 'first_name': 'John', 'last_name': 'Smith'}
    )
    client_user.set_password('password123')
    client_user.save()

    # 2. Create Properties
    print("Creating Properties...")
    
    properties_data = [
        {
            'title': 'Luxury Villa in Karen',
            'description': 'A stunning 5-bedroom villa with a large garden, swimming pool, and modern amenities. Located in a serene environment perfect for families.',
            'property_type': 'villa',
            'listing_type': 'sale',
            'status': 'available',
            'price': Decimal('85000000.00'),
            'city': 'Nairobi',
            'address': 'Karen Road, Nairobi',
            'bedrooms': 5,
            'bathrooms': 4.5,
            'area_sqft': 4500,
            'land_size_acres': 0.5,
            'has_swimming_pool': True,
            'has_garden': True,
            'has_security': True,
            'has_parking': True,
            'parking_spaces': 4
        },
        {
            'title': 'Modern Apartment in Kilimani',
            'description': 'Chic 2-bedroom apartment in the heart of Kilimani. Close to shopping malls, schools, and hospitals. Ideal for young professionals.',
            'property_type': 'apartment',
            'listing_type': 'rent',
            'status': 'available',
            'price': Decimal('85000.00'),
            'city': 'Nairobi',
            'address': 'Argwings Kodhek Road',
            'bedrooms': 2,
            'bathrooms': 2,
            'area_sqft': 1200,
            'has_elevator': True,
            'has_gym': True,
            'has_security': True,
            'has_parking': True,
            'parking_spaces': 1
        },
        {
            'title': 'Prime Commercial Land in Thika',
            'description': '1-acre commercial land located along Thika Superhighway. Perfect for a shopping mall or office complex.',
            'property_type': 'commercial_land',
            'listing_type': 'sale',
            'status': 'available',
            'price': Decimal('45000000.00'),
            'city': 'Thika',
            'address': 'Thika Superhighway',
            'land_size_acres': 1.0,
            'zoning_type': 'commercial',
            'has_road_access': True,
            'has_electricity': True,
            'has_water_connection': True
        },
        {
            'title': 'Cozy Bungalow in Mombasa',
            'description': '3-bedroom bungalow just minutes from the beach. Features a spacious living area and a beautiful patio.',
            'property_type': 'bungalow',
            'listing_type': 'sale',
            'status': 'sold',
            'price': Decimal('12500000.00'),
            'city': 'Mombasa',
            'address': 'Nyali Beach Road',
            'bedrooms': 3,
            'bathrooms': 2,
            'area_sqft': 1800,
            'land_size_acres': 0.25,
            'has_garden': True,
            'is_waterfront': False
        },
        {
            'title': 'Office Space in Westlands',
            'description': 'Premium office space in a high-rise building. Fully furnished with conference rooms and high-speed internet.',
            'property_type': 'office',
            'listing_type': 'rent',
            'status': 'available',
            'price': Decimal('150000.00'),
            'city': 'Nairobi',
            'address': 'Westlands Road',
            'area_sqft': 2000,
            'has_elevator': True,
            'has_security': True,
            'has_parking': True,
            'has_air_conditioning': True
        }
    ]

    for p_data in properties_data:
        # Default coords for map (Nairobi approx)
        lat = Decimal('-1.2921') + Decimal(random.uniform(-0.05, 0.05))
        lng = Decimal('36.8219') + Decimal(random.uniform(-0.05, 0.05))
        
        prop, created = Property.objects.get_or_create(
            title=p_data['title'],
            defaults={
                **p_data,
                'owner': agent_user,
                'latitude': lat,
                'longitude': lng,
                'zipcode': '00100',
                'state': 'Nairobi County'
            }
        )
        
        if created:
            print(f"  Created: {prop.title}")
            
            # 3. Create Booking Settings for each property
            BookingSettings.objects.create(
                listing=prop,
                max_viewers_per_slot=5,
                slot_duration_minutes=60,
                start_hour=8,
                end_hour=17
            )

            # 4. Add Dummy Image (Using a placeholder URL approach in templates, 
            # but creating the record here so the loop works)
            # In a real seed, you'd save actual files. 
            # We will create one record without a file or skip to avoid errors if file missing.
            # PropertyImage.objects.create(property=prop, is_primary=True, caption="Main View")

    # 5. Create Bookings & Inquiries
    print("Creating Interactions...")
    
    # Inquiry
    available_props = Property.objects.filter(status='available')
    if available_props.exists():
        p = available_props.first()
        Inquiry.objects.get_or_create(
            property=p,
            user=client_user,
            defaults={
                'inquirer_name': 'John Smith',
                'inquirer_email': 'john@client.com',
                'message': 'Is this property still available for viewing this weekend?',
                'status': 'new'
            }
        )
        
        # Booking
        start_time = timezone.now() + timedelta(days=2, hours=3)
        Booking.objects.get_or_create(
            user=client_user,
            listing=p,
            defaults={
                'start_datetime': start_time,
                'end_datetime': start_time + timedelta(hours=1),
                'status': 'pending',
                'notes': 'I will be coming with my spouse.'
            }
        )
        
        # Favorite
        Favorite.objects.get_or_create(user=client_user, property=p)

    print("✅ Database Seeded Successfully!")

if __name__ == '__main__':
    run_seed()