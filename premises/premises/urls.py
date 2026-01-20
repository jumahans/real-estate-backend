from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from app.views import NotificationListView, mark_as_read, send_notification


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
<<<<<<< HEAD
    path('', include('app.urls')),
=======
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('api/notifications/<int:notification_id>/read/', mark_as_read, name='mark-as-read'),
    path('api/notifications/send/', send_notification, name='send-notification'),
>>>>>>> 159270cf6c92692f663edc17db73bbe757aa205d
]
