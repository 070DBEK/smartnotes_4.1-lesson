from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import User, Profile, Follow
from .serializers import (
    UserCreateSerializer, UserLoginSerializer, UserSerializer,
    ProfileSerializer, ProfileUpdateSerializer, EmailVerificationSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        verification_url = f"{settings.SITE_URL}/api/v1/auth/verify-email/?token={user.verification_token}"
        send_mail(
            'Verify your email',
            f'Click here to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    serializer = EmailVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.validated_data['token']

    try:
        user = User.objects.get(verification_token=token)
        user.is_verified = True
        user.verification_token = None
        user.save()
        return Response({'detail': 'Email verified successfully'})
    except User.DoesNotExist:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Logout successful'})
    except Exception:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']

    try:
        user = User.objects.get(email=email)
        reset_token = user.generate_reset_token()

        reset_url = f"{settings.SITE_URL}/api/v1/auth/password-reset/confirm/?token={reset_token}"
        send_mail(
            'Password Reset',
            f'Click here to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

        return Response({'detail': 'Password reset email sent'})
    except User.DoesNotExist:
        return Response({'detail': 'Password reset email sent'})  # Don't reveal if email exists


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data['token']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(reset_token=token)
        user.set_password(password)
        user.reset_token = None
        user.save()
        return Response({'detail': 'Password reset successful'})
    except User.DoesNotExist:
        return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    queryset = Profile.objects.all()
    permission_classes = [permissions.AllowAny]


class CurrentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProfileUpdateSerializer
        return ProfileSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return Response({'detail': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user.profile
    )

    if not created:
        return Response({'detail': 'Already following'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(ProfileSerializer(target_user.profile).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return Response({'detail': 'Cannot unfollow yourself'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        follow = Follow.objects.get(follower=request.user, following=target_user.profile)
        follow.delete()
        return Response(ProfileSerializer(target_user.profile).data)
    except Follow.DoesNotExist:
        return Response({'detail': 'Not following'}, status=status.HTTP_400_BAD_REQUEST)


class FollowersListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        follower_ids = Follow.objects.filter(following=user.profile).values_list('follower', flat=True)
        return Profile.objects.filter(user__id__in=follower_ids)


class FollowingListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        following_ids = Follow.objects.filter(follower=user).values_list('following', flat=True)
        return Profile.objects.filter(id__in=following_ids)
