import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser, PermissionsMixin
from django.db.models import OneToOneField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name}"


def chat_room_password(value):
        if len(value)<8:
            raise ValidationError('Password must contain at least 8 characters')
        if not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain letters and numbers')

class ChatRoom(models.Model):
    members = models.ManyToManyField(Profile, related_name='room')
    name = models.CharField(max_length=225)
    password = models.CharField(max_length=120, validators=[chat_room_password])
    created_at = models.DateTimeField(auto_now_add=True)



class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', default=1)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sent_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
         return f"{self.sender}: {self.content[:30]}"
