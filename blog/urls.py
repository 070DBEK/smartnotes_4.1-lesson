from django.urls import path
from . import views

urlpatterns = [
    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:id>/like/', views.like_post, name='like_post'),
    path('posts/<int:id>/unlike/', views.unlike_post, name='unlike_post'),

    # Comments
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment_detail'),
    path('comments/<int:id>/like/', views.like_comment, name='like_comment'),
    path('comments/<int:id>/unlike/', views.unlike_comment, name='unlike_comment'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:id>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_read'),
    path('notifications/mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_read'),

    # Search
    path('search/', views.search, name='search'),
]
