from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

def avatar_upload_to(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    uid = models.CharField(max_length=24, blank=True, default='')
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)
    bio = models.TextField(blank=True)
    # Redes sociais com JSON
    socials = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = get_random_string(8)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Profile: {self.user.username}'
