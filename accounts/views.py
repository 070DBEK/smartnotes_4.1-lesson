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
from .email_templates import get_password_reset_email, get_verification_email, get_welcome_email


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            try:
                email_html = get_verification_email(
                    username=user.username,
                    verification_token=user.verification_token,
                    site_url=settings.SITE_URL
                )

                send_mail(
                    subject='🎉 Zamka ga xush kelibsiz! Email ni tasdiqlang',
                    message=f'Assalomu alaykum {user.username}! Email tasdiqlash tokeni: {user.verification_token}',
                    html_message=email_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email yuborishda xatolik: {e}")

            return Response({
                'message': 'Foydalanuvchi muvaffaqiyatli yaratildi. Email manzilingizni tasdiqlash uchun emailingizni tekshiring.',
                'user': UserSerializer(user).data,
                'verification_token': user.verification_token  # Development uchun
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Zamka ga xush kelibsiz! Muvaffaqiyatli tizimga kirdingiz.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    serializer = EmailVerificationSerializer(data=request.data)

    if serializer.is_valid():
        token = serializer.validated_data['token']

        try:
            user = User.objects.get(verification_token=token)

            if user.is_verified:
                return Response({
                    'message': 'Email manzil allaqachon tasdiqlangan.'
                }, status=status.HTTP_200_OK)

            user.is_verified = True
            user.verification_token = None
            user.save()

            try:
                welcome_html = get_welcome_email(username=user.username)
                send_mail(
                    subject='🎊 Zamka oilasiga xush kelibsiz!',
                    message=f'Tabriklaymiz {user.username}! Zamka ga muvaffaqiyatli qo\'shildingiz.',
                    html_message=welcome_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Welcome email yuborishda xatolik: {e}")

            return Response({
                'message': 'Email manzil muvaffaqiyatli tasdiqlandi. Endi Zamka ga kirishingiz mumkin!'
            })

        except User.DoesNotExist:
            return Response({
                'error': 'Noto\'g\'ri yoki eskirgan token.'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({
                'error': 'Refresh token kiritish majburiy.'
            }, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            'message': 'Zamka dan muvaffaqiyatli chiqdingiz. Qaytib kelishingizni kutamiz!'
        })
    except Exception:
        return Response({
            'error': 'Noto\'g\'ri token.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            reset_token = user.generate_reset_token()

            email_html = get_password_reset_email(
                username=user.username,
                reset_token=reset_token,
                site_url=settings.SITE_URL
            )

            send_mail(
                subject='🔐 Zamka - Parolni tiklash',
                message=f'Assalomu alaykum {user.username}! Parol tiklash tokeni: {reset_token}',
                html_message=email_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        except User.DoesNotExist:
            pass

        return Response({
            'message': 'Agar email manzil Zamka da ro\'yxatdan o\'tgan bo\'lsa, parolni tiklash bo\'yicha ko\'rsatma yuborildi.'
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)

    if serializer.is_valid():
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(reset_token=token)
            user.set_password(password)
            user.reset_token = None
            user.save()

            return Response({
                'message': 'Parol muvaffaqiyatli o\'zgartirildi. Endi yangi parol bilan Zamka ga kirishingiz mumkin!'
            })

        except User.DoesNotExist:
            return Response({
                'error': 'Noto\'g\'ri yoki eskirgan token.'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({
            'error': 'O\'zingizni kuzata olmaysiz.'
        }, status=status.HTTP_400_BAD_REQUEST)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user.profile
    )

    if not created:
        return Response({
            'error': 'Siz allaqachon bu foydalanuvchini kuzatyapsiz.'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'message': f'{target_user.username} muvaffaqiyatli kuzatildi.',
        'profile': ProfileSerializer(target_user.profile).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return Response({
            'error': 'O\'zingizni kuzatishni to\'xtata olmaysiz.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        follow = Follow.objects.get(follower=request.user, following=target_user.profile)
        follow.delete()
        return Response({
            'message': f'{target_user.username} kuzatishdan chiqarildi.',
            'profile': ProfileSerializer(target_user.profile).data
        })
    except Follow.DoesNotExist:
        return Response({
            'error': 'Siz bu foydalanuvchini kuzatmayapsiz.'
        }, status=status.HTTP_400_BAD_REQUEST)


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
