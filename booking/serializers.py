from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta, time
from django.contrib.auth import get_user_model
from .models import Property, Booking, Agent, Profile
from django.db import transaction
User = get_user_model()

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'name', 'phone']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'phone']

class PropertySerializer(serializers.ModelSerializer):
    available_slots = serializers.SerializerMethodField()
    agent = AgentSerializer(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'

    def get_available_slots(self, obj):
        """Generate next 10 available 1-hour slots (9AM-6PM)"""
        now = timezone.now()
        slots = []
        current_date = now.date()
        
        for day_offset in range(7):  # Next 7 days
            for hour in range(9, 18):  # 9AM to 6PM
                start = timezone.make_aware(
                    timezone.datetime(
                        current_date.year, current_date.month, current_date.day,
                        hour, 0, 0
                    )
                )
                end = start + timedelta(hours=1)
                
                # Count overlaps
                overlaps = obj.bookings.filter(
                    start_datetime__lt=end,
                    end_datetime__gt=start,
                    status__in=['pending', 'confirmed']
                ).count()
                
                if overlaps < obj.max_viewers:
                    slots.append({
                        'start': start.isoformat(),
                        'end': end.isoformat(),
                        'available': obj.max_viewers - overlaps
                    })
            
            current_date += timedelta(days=1)
            if len(slots) >= 10:
                break
        
        return slots[:10]

class BookingSerializer(serializers.ModelSerializer):
    agents = AgentSerializer(many=True, read_only=True)
    profile = ProfileSerializer(read_only=True)
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['version', 'created_at', 'agents']

    def validate(self, data):
        """Trigger model validation (clean())"""
        booking = Booking(**data)
        booking.full_clean()  # Calls your overlaps/past-date/max_viewers logic
        return data

    def create(self, validated_data):
        """Auto-assign user from request.user if not provided"""
        validated_data['user'] = self.context['request'].user
        with transaction.atomic():
            return super().create(validated_data)
