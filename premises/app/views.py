from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from django.contrib.auth.models import User

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.notifications.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return Response({'status': 'marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    recipient_id = request.data.get('recipient_id')
    verb = request.data.get('verb')
    description = request.data.get('description')
    try:
        recipient = User.objects.get(id=recipient_id)
        Notification.objects.create(recipient=recipient, verb=verb, description=description)
        return Response({'status': 'notification sent'})
    except User.DoesNotExist:
        return Response({'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)

