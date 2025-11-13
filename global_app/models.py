from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

def avatar_upload_to(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

def post_image_upload_to(instance, filename):
    return f'posts/user_{instance.author.id}/{filename}'

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


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=5000)
    image = models.ImageField(upload_to=post_image_upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
    
    def __str__(self):
        return f'{self.author.username} - {self.content[:50]}'
    
    def total_likes(self):
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Verifica se o usuário curtiu este post"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        verbose_name = 'Curtida'
        verbose_name_plural = 'Curtidas'
    
    def __str__(self):
        return f'{self.user.username} curtiu post de {self.post.author.username}'