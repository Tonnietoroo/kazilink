from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    usertype = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    contact = models.CharField(max_length=15, blank=True, null=True)
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    suspended = models.BooleanField(default=False)  # New field

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user receiving the notification
    notification_text = models.TextField()  # Notification content (e.g., "You have a new appointment")
    link = models.URLField(null=True, blank=True)  # Optional link to view the related resource (like appointment)
    created_at = models.DateTimeField(default=now)  # When the notification was created
    is_read = models.BooleanField(default=False)  # To track read/unread status

    def _str_(self):
        return f"Notification for {self.user.username} - {self.notification_text[:50]}"
