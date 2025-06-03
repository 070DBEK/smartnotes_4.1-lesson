from django.urls import path
from . import views


urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/stats/', views.notification_stats, name='notification-stats'),
    path('notifications/unread/', views.unread_notifications, name='unread-notifications'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark-all-read'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear-all-notifications'),
    path('notifications/<int:pk>/mark-as-read/', views.mark_notification_as_read, name='mark-notification-read'),
    path('notifications/<int:pk>/delete/', views.delete_notification, name='delete-notification'),
    path('notification-settings/', views.NotificationSettingsView.as_view(), name='notification-settings'),
    path('notifications/test/', views.test_notification, name='test-notification'),
]