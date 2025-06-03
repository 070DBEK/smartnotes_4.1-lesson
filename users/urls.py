from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('password-reset/', views.password_reset, name='password-reset'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password-reset-confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('me/', views.current_user, name='current-user'),

    path('profiles/me/', views.CurrentProfileView.as_view(), name='current-profile'),
    path('profiles/<str:username>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<str:username>/follow/', views.follow_user, name='follow-user'),
    path('profiles/<str:username>/unfollow/', views.unfollow_user, name='unfollow-user'),
    path('profiles/<str:username>/followers/', views.FollowersListView.as_view(), name='user-followers'),
    path('profiles/<str:username>/following/', views.FollowingListView.as_view(), name='user-following'),
]