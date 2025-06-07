from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
import uuid
import os


def profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profiles', str(instance.user.id), filename)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    email = models.EmailField(unique=True, error_messages={
        'unique': "Bu email manzil allaqachon ro'yxatdan o'tgan."
    })
    username = models.CharField(max_length=150, unique=True, error_messages={
        'unique': "Bu username allaqachon band."
    })
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = get_random_string(50)
        super().save(*args, **kwargs)

    def generate_reset_token(self):
        self.reset_token = get_random_string(50)
        self.save()
        return self.reset_token

    def clean(self):
        super().clean()
        if self.email and User.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError({
                'email': "Bu email manzil allaqachon ro'yxatdan o'tgan."
            })
        if self.username and User.objects.filter(username=self.username).exclude(pk=self.pk).exists():
            raise ValidationError({
                'username': "Bu username allaqachon band."
            })


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, max_length=500)
    image = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def clean(self):
        if self.follower == self.following.user:
            raise ValidationError("Foydalanuvchi o'zini kuzata olmaydi.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.user.username}"
