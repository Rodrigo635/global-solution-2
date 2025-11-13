from django.contrib import admin
from .models import Profile, Post, Like

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'uid', 'bio_preview']
    search_fields = ['user__username', 'user__email', 'uid']
    list_filter = ['user__date_joined']
    readonly_fields = ['uid']
    
    def bio_preview(self, obj):
        """Mostra preview da bio"""
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '-'
    bio_preview.short_description = 'Bio'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'created_at', 'total_likes']
    search_fields = ['author__username', 'content']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        """Mostra preview do conteúdo"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteúdo'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'post__content']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'