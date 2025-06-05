from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    path('users/me/', views.CurrentUserView.as_view(), name='current_user'),
    path('profiles/me/', views.CurrentProfileView.as_view(), name='current_profile'),
    path('profiles/<str:username>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profiles/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profiles/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('profiles/<str:username>/followers/', views.FollowersListView.as_view(), name='followers'),
    path('profiles/<str:username>/following/', views.FollowingListView.as_view(), name='following'),
]
