from django.urls import path
from . import views


urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),

    path('posts/<int:pk>/like/', views.like_post, name='like-post'),
    path('posts/<int:pk>/unlike/', views.unlike_post, name='unlike-post'),

    path('users/<str:username>/posts/', views.UserPostsView.as_view(), name='user-posts'),
    path('my-posts/', views.my_posts, name='my-posts'),
    path('feed/', views.feed, name='feed'),
]