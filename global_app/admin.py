from django.contrib import admin
from .models import Profile, Post, Like, Friendship, FriendRequest, Opportunity, Application

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

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['user', 'friend', 'created_at']
    search_fields = ['user__username', 'friend__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'company', 'status', 'total_applications', 'deadline', 'created_at']
    list_filter = ['type', 'status', 'created_at', 'work_mode']
    search_fields = ['title', 'company', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'type', 'status', 'description')
        }),
        ('Detalhes da Oportunidade', {
            'fields': ('company', 'location', 'work_mode', 'salary_range', 'deadline')
        }),
        ('Requisitos', {
            'fields': ('requirements', 'skills'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Automaticamente define quem criou a oportunidade"""
        if not change:
            obj.created_by = request.user # Se for uma nova oportunidade
        super().save_model(request, obj, form, change)
    
    def total_applications(self, obj):
        """Mostra total de inscrições"""
        return obj.total_applications()
    total_applications.short_description = 'Inscrições'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'opportunity_title', 'opportunity_type', 'status', 'applied_at']
    list_filter = ['status', 'applied_at', 'opportunity__type']
    search_fields = ['user__username', 'user__email', 'opportunity__title']
    date_hierarchy = 'applied_at'
    readonly_fields = ['applied_at', 'updated_at']
    
    fieldsets = (
        ('Informações da Inscrição', {
            'fields': ('opportunity', 'user', 'status')
        }),
        ('Documentos', {
            'fields': ('cover_letter', 'resume')
        }),
        ('Avaliação', {
            'fields': ('admin_notes',)
        }),
        ('Datas', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def opportunity_title(self, obj):
        """Mostra o título da oportunidade"""
        return obj.opportunity.title
    opportunity_title.short_description = 'Oportunidade'
    
    def opportunity_type(self, obj):
        """Mostra o tipo da oportunidade"""
        return obj.opportunity.get_type_display()
    opportunity_type.short_description = 'Tipo'
    
    actions = ['mark_as_reviewing', 'mark_as_accepted', 'mark_as_rejected']
    
    def mark_as_reviewing(self, request, queryset):
        """Marca inscrições como 'Em Análise'"""
        updated = queryset.update(status='reviewing')
        self.message_user(request, f'{updated} inscrição(ões) marcada(s) como Em Análise.')
    mark_as_reviewing.short_description = 'Marcar como Em Análise'
    
    def mark_as_accepted(self, request, queryset):
        """Marca inscrições como 'Aceito'"""
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} inscrição(ões) aceita(s).')
    mark_as_accepted.short_description = 'Marcar como Aceito'
    
    def mark_as_rejected(self, request, queryset):
        """Marca inscrições como 'Rejeitado'"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} inscrição(ões) rejeitada(s).')
    mark_as_rejected.short_description = 'Marcar como Rejeitado'