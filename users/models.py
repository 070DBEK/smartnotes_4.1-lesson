from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('author', 'Author'),
        ('reader', 'Reader')
    ], default='reader')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email