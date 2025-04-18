# From https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#a-full-example

from core.models import BaseModel
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email and password.

        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), name=name)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            name=name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, BaseModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class NotificationSettings(models.Model):
    """
    Model to store user notification preferences
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Notification types
    signal_notifications = models.BooleanField(default=True)
    
    # Notification methods
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sound_alerts = models.BooleanField(default=True)
    
    # Alert types
    signal_alerts = models.BooleanField(default=True)
    price_alerts = models.BooleanField(default=True)
    pattern_recognition = models.BooleanField(default=True)
    economic_news_alerts = models.BooleanField(default=False)
    
    # Signal frequency
    max_signals_per_day = models.IntegerField(default=15)
    
    # Signal quality filter - options: high, medium, all
    QUALITY_CHOICES = [
        ('high', 'High quality signals only (70%+ confidence)'),
        ('medium', 'Medium and high quality (50%+ confidence)'),
        ('all', 'All signals')
    ]
    signal_quality_filter = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='high')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification settings for {self.user.email}"
