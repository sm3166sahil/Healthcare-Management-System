from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Profile extension for the built-in Django User model.
    Stores application roles, phone numbers, and department details.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('analyst', 'Data Analyst'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='analyst')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a corresponding UserProfile when a new User is created,
    and save profile on user updates.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Save profile if it exists, or create if missing
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)
