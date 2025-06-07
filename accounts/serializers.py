from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from .models import User, Profile, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active', 'is_staff', 'is_verified', 'date_joined', 'role']
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_verified', 'date_joined', 'role']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'required': 'Email manzil kiritish majburiy.',
                    'invalid': 'To\'g\'ri email manzil kiriting.',
                    'unique': 'Bu email manzil allaqachon ro\'yxatdan o\'tgan.'
                }
            },
            'username': {
                'error_messages': {
                    'required': 'Username kiritish majburiy.',
                    'unique': 'Bu username allaqachon band.'
                }
            }
        }

    def validate_email(self, value):
        """Email validation"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email manzil allaqachon ro'yxatdan o'tgan.")
        return value.lower()

    def validate_username(self, value):
        """Username validation"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username allaqachon band.")
        if len(value) < 3:
            raise serializers.ValidationError("Username kamida 3 ta belgidan iborat bo'lishi kerak.")
        return value

    def validate_password(self, value):
        """Password strength validation"""
        if len(value) < 8:
            raise serializers.ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")

        try:
            validate_password(value)
        except DjangoValidationError as e:
            error_messages = []
            for message in e.messages:
                if "too common" in message.lower():
                    error_messages.append("Bu parol juda oddiy.")
                elif "too similar" in message.lower():
                    error_messages.append("Parol foydalanuvchi ma'lumotlariga juda o'xshash.")
                elif "entirely numeric" in message.lower():
                    error_messages.append("Parol faqat raqamlardan iborat bo'lmasligi kerak.")
                else:
                    error_messages.append(message)
            raise serializers.ValidationError(error_messages)
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Parollar mos kelmaydi."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        try:
            user = User(
                email=validated_data['email'].lower(),
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.full_clean()  
            user.save()

            return user

        except IntegrityError as e:
            if 'email' in str(e).lower():
                raise serializers.ValidationError({
                    'email': "Bu email manzil allaqachon ro'yxatdan o'tgan."
                })
            elif 'username' in str(e).lower():
                raise serializers.ValidationError({
                    'username': "Bu username allaqachon band."
                })
            else:
                raise serializers.ValidationError({
                    'non_field_errors': ["Foydalanuvchi yaratishda xatolik yuz berdi."]
                })
        except DjangoValidationError as e:
            # Handle model validation errors
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(e.error_dict)
            else:
                raise serializers.ValidationError({
                    'non_field_errors': [str(e)]
                })


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': 'Email manzil kiritish majburiy.',
            'invalid': 'To\'g\'ri email manzil kiriting.'
        }
    )
    password = serializers.CharField(
        error_messages={
            'required': 'Parol kiritish majburiy.'
        }
    )

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({
                "non_field_errors": ["Email va parol kiritish majburiy."]
            })

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "Bu email manzil bilan foydalanuvchi topilmadi."
            })

        if not user_obj.is_verified:
            raise serializers.ValidationError({
                "email": "Iltimos, avval email manzilingizni tasdiqlang."
            })

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({
                "password": "Noto'g'ri parol."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": ["Foydalanuvchi hisobi faol emas."]
            })

        attrs['user'] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'image', 'followers_count', 'following_count']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'image']

    def validate_bio(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("Bio 500 belgidan oshmasligi kerak.")
        return value


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(
        error_messages={
            'required': 'Token kiritish majburiy.',
            'blank': 'Token bo\'sh bo\'lmasligi kerak.'
        }
    )


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': 'Email manzil kiritish majburiy.',
            'invalid': 'To\'g\'ri email manzil kiriting.'
        }
    )


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(
        error_messages={
            'required': 'Token kiritish majburiy.'
        }
    )
    password = serializers.CharField(
        min_length=8,
        error_messages={
            'required': 'Parol kiritish majburiy.',
            'min_length': 'Parol kamida 8 ta belgidan iborat bo\'lishi kerak.'
        }
    )
    password_confirm = serializers.CharField(
        error_messages={
            'required': 'Parolni takrorlash majburiy.'
        }
    )

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            error_messages = []
            for message in e.messages:
                if "too common" in message.lower():
                    error_messages.append("Bu parol juda oddiy.")
                elif "too similar" in message.lower():
                    error_messages.append("Parol foydalanuvchi ma'lumotlariga juda o'xshash.")
                elif "entirely numeric" in message.lower():
                    error_messages.append("Parol faqat raqamlardan iborat bo'lmasligi kerak.")
                else:
                    error_messages.append(message)
            raise serializers.ValidationError(error_messages)
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Parollar mos kelmaydi."
            })
        return attrs
