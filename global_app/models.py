from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

def avatar_upload_to(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

def post_image_upload_to(instance, filename):
    return f'posts/user_{instance.author.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    uid = models.CharField(max_length=24, blank=True, default='')
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)
    bio = models.TextField(blank=True)
    # Redes sociais com JSON (Não terminei de implementar)
    socials = models.JSONField(default=list, blank=True)
    # Preferências de acessibilidade e configurações
    dark_mode = models.BooleanField(default=False)
    vlibras_enabled = models.BooleanField(default=False)
    font_size = models.CharField(
        max_length=10, 
        choices=[
            ('small', 'Pequeno'),
            ('medium', 'Médio'),
            ('large', 'Grande'),
        ],
        default='medium'
    )
    # Status da conta
    last_activity = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = get_random_string(8)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Profile: {self.user.username}'
    
    def is_online(self):
        """Verifica se o usuário está online (ativo nos últimos 5 minutos)"""
        if not self.last_activity:
            return False
        time_threshold = timezone.now() - timedelta(minutes=5)
        return self.last_activity > time_threshold
    
    def update_last_activity(self):
        """Atualiza o timestamp de última atividade"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

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
    
class Friendship(models.Model):
    """Modelo para armazenar amizades confirmadas"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'friend')
        ordering = ['-created_at']
        verbose_name = 'Amizade'
        verbose_name_plural = 'Amizades'
    
    def __str__(self):
        return f'{self.user.username} é amigo de {self.friend.username}'

class FriendRequest(models.Model):
    """Modelo para solicitações de amizade"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('rejected', 'Rejeitado'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
        verbose_name = 'Solicitação de Amizade'
        verbose_name_plural = 'Solicitações de Amizade'
    
    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username} ({self.status})'
    
    def accept(self):
        """Aceita a solicitação e cria a amizade bidirecional"""
        self.status = 'accepted'
        self.save()
        
        # Criar amizade pros 2 lados
        Friendship.objects.get_or_create(user=self.from_user, friend=self.to_user)
        Friendship.objects.get_or_create(user=self.to_user, friend=self.from_user)
    
    def reject(self):
        """Rejeita a solicitação"""
        self.status = 'rejected'
        self.delete()
    
    def cancel(self):
        """Cancela a solicitação (quem enviou pode cancelar)"""
        self.delete()

class Opportunity(models.Model):
    """Modelo para oportunidades (vagas, entrevistas, demandas)"""
    TYPE_CHOICES = [
        ('job', 'Vaga de Emprego'),
        ('interview', 'Oportunidade de Entrevista'),
        ('demand', 'Demanda/Projeto'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Aberta'),
        ('closed', 'Fechada'),
        ('paused', 'Pausada'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descrição')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='job', verbose_name='Tipo')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='Status')
    company = models.CharField(max_length=200, verbose_name='Empresa/Cliente', blank=True)
    location = models.CharField(max_length=200, verbose_name='Localização', blank=True)
    salary_range = models.CharField(max_length=100, verbose_name='Faixa Salarial', blank=True)
    work_mode = models.CharField(max_length=50, verbose_name='Modo de Trabalho', blank=True, help_text='Ex: Remoto, Híbrido, Presencial')
    requirements = models.TextField(verbose_name='Requisitos', blank=True)
    skills = models.CharField(max_length=500, verbose_name='Habilidades', blank=True, help_text='Separe por vírgula')
    deadline = models.DateField(verbose_name='Prazo de Inscrição', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_opportunities', verbose_name='Criado por')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.title}'
    
    def total_applications(self):
        """Retorna o total de inscrições"""
        return self.applications.count()
    
    def is_expired(self):
        """Verifica se a oportunidade está expirada"""
        if self.deadline:
            from django.utils import timezone
            return timezone.now().date() > self.deadline
        return False

class Application(models.Model):
    """Modelo para inscrições em oportunidades"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('reviewing', 'Em Análise'),
        ('accepted', 'Aceito'),
        ('rejected', 'Rejeitado'),
    ]
    
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications', verbose_name='Oportunidade')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', verbose_name='Usuário')
    cover_letter = models.TextField(verbose_name='Carta de Apresentação', blank=True)
    resume = models.FileField(upload_to='resumes/', verbose_name='Currículo', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='Data da Inscrição')
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(verbose_name='Notas do Administrador', blank=True)
    
    class Meta:
        unique_together = ('opportunity', 'user')
        ordering = ['-applied_at']
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
    
    def __str__(self):
        return f'{self.user.username} - {self.opportunity.title}'