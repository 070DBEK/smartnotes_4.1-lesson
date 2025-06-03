from django.urls import path
from . import views

urlpatterns = [
    # Comments for specific post
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='post-comments'),

    # Comment detail operations
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),

    # Like/Unlike comments
    path('comments/<int:pk>/like/', views.like_comment, name='like-comment'),
    path('comments/<int:pk>/unlike/', views.unlike_comment, name='unlike-comment'),

    # Comment replies
    path('comments/<int:pk>/replies/', views.comment_replies, name='comment-replies'),

    # User specific comments
    path('users/<str:username>/comments/', views.UserCommentsView.as_view(), name='user-comments'),
    path('my-comments/', views.my_comments, name='my-comments'),
]