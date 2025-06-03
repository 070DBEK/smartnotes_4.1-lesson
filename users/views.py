from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Follow, EmailVerificationToken, PasswordResetToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProfileSerializer, ProfileUpdateSerializer,
    EmailVerificationSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create email verification token
        verification_token = EmailVerificationToken.objects.create(user=user)

        # Send verification email (in production)
        if not settings.DEBUG:
            send_mail(
                'Verify your email',
                f'Your verification token: {verification_token.token}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

        return Response(
            {
                'user': UserSerializer(user).data,
                'message': 'User created successfully. Please verify your email.',
                'verification_token': str(verification_token.token) if settings.DEBUG else None
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        return Response({
            'user': UserSerializer(validated_data['user']).data,
            'tokens': validated_data['tokens']
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    serializer = EmailVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data['token']
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        if verification_token.is_expired():
            verification_token.delete()
            return Response(
                {'detail': 'Token has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = verification_token.user
        user.email_verified = True
        user.save()
        verification_token.delete()

        return Response({'detail': 'Email verified successfully'})
    except EmailVerificationToken.DoesNotExist:
        return Response(
            {'detail': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Logout successful'})
    except TokenError:
        return Response(
            {'detail': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# Profile Views
class CurrentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return ProfileUpdateSerializer
        return ProfileSerializer


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    queryset = Profile.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return Response(
            {'detail': 'Cannot follow yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user.profile
    )

    if not created:
        return Response(
            {'detail': 'Already following this user'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(ProfileSerializer(target_user.profile, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return Response(
            {'detail': 'Cannot unfollow yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        follow = Follow.objects.get(
            follower=request.user,
            following=target_user.profile
        )
        follow.delete()
        return Response(ProfileSerializer(target_user.profile, context={'request': request}).data)
    except Follow.DoesNotExist:
        return Response(
            {'detail': 'Not following this user'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowersListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Profile.objects.filter(followers__follower=user)


class FollowingListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Profile.objects.filter(user__following__following=user.profile)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    user = User.objects.get(email=email)

    # Delete old tokens
    PasswordResetToken.objects.filter(user=user).delete()

    # Create new token
    reset_token = PasswordResetToken.objects.create(user=user)

    # Send email (in production)
    if not settings.DEBUG:
        send_mail(
            'Password Reset',
            f'Your password reset token: {reset_token.token}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    return Response({
        'detail': 'Password reset email sent',
        'reset_token': str(reset_token.token) if settings.DEBUG else None
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data['token']
    password = serializer.validated_data['password']

    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_expired():
            reset_token.delete()
            return Response(
                {'detail': 'Token has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = reset_token.user
        user.set_password(password)
        user.save()
        reset_token.delete()

        return Response({'detail': 'Password reset successful'})
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'detail': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )