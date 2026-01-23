from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Property, Booking
from .serializers import PropertySerializer, BookingSerializer

class PropertyViewSet(viewsets.ModelViewSet):
    # This queryset fixes the "basename" assertion error
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def slots(self, request, pk=None):
        """Custom endpoint to get available slots for a property"""
        property_obj = self.get_object()
        serializer = self.get_serializer(property_obj)
        # Using the serializer method we defined earlier
        return Response(serializer.data.get('available_slots', []))

class BookingViewSet(viewsets.ModelViewSet):
    # Base queryset required by router
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter bookings to only show the logged-in user's
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign user on create
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Version locking handled in model.save(), but atomic block here is good practice
        with transaction.atomic():
            serializer.save()
