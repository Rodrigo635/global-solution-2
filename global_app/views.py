from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .forms import SignUpForm, PostForm
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth.models import User
from .models import Post, Like, Profile
from django.views.decorators.http import require_POST
import json

def home(request):
    return render(request, 'pages/home.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            messages.success(request, "Conta criada com sucesso. Você já está logado.")
            auth_login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Por favor corrija os erros no formulário.")
    else:
        form = SignUpForm()
    return render(request, 'pages/signup.html', {'form': form})

def login(request):
    if request.method == 'GET':
        # Descartar mensagens pendentes
        list(messages.get_messages(request))

    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Olá {user.first_name or user.username} - você entrou com sucesso.")
            return redirect(next_url or reverse('feed'))
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'pages/login.html', {'form': form, 'next': next_url})

def logout(request):
    auth_logout(request)
    messages.info(request, "Você saiu da conta.")
    return redirect('home')

@login_required
def profile(request, username=None):
    # Se username não informado, mostra o perfil do usuário logado
    if username:
        # Ver o perfil público
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = getattr(user, 'profile', None)
    
    # Criar perfil se não existir
    if not profile and user == request.user:
        profile = Profile.objects.create(user=user)
    
    context = {'user': user, 'profile': profile}

    return render(request, 'pages/profile.html', context)

@login_required
def feed(request):
    suggested_users = User.objects.exclude(id=request.user.id).select_related('profile')[:5]
    
    # Buscar todos os posts (ordenados por data)
    posts = Post.objects.select_related('author', 'author__profile').prefetch_related('likes')
    
    # Adicionar informação se o usuário curtiu cada post
    for post in posts:
        post.user_has_liked = post.likes.filter(user=request.user).exists()
    
    # Formulário para criar novo post
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post criado com sucesso!')
            return redirect('feed')
    else:
        form = PostForm()
    
    context = {
        'suggested_users': suggested_users,
        'posts': posts,
        'form': form
    }
    return render(request, 'pages/feed.html', context)

@login_required
def calls(request):
    suggested_users = User.objects.exclude(id=request.user.id).select_related('profile')[:5]
    
    context = {
        'suggested_users': suggested_users
    }
    return render(request, 'pages/calls.html', context)

@login_required
def chat(request):
    return render(request, 'pages/chat.html')

@login_required
def toggle_like(request, post_id):
    """View para curtir/descurtir um post via AJAX"""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            # Se já curtiu, remove a curtida
            like.delete()
            liked = False
        else:
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes()
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
@require_POST
def update_dark_mode(request):
    """Atualiza preferência de modo escuro"""
    try:
        data = json.loads(request.body)
        enabled = data.get('enabled', False)
        
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.dark_mode = enabled
        profile.save()
        
        return JsonResponse({'success': True, 'dark_mode': enabled})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def update_vlibras(request):
    """Atualiza preferência de V-Libras"""
    try:
        data = json.loads(request.body)
        enabled = data.get('enabled', False)
        
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.vlibras_enabled = enabled
        profile.save()
        
        return JsonResponse({'success': True, 'vlibras_enabled': enabled})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def update_font_size(request):
    """Atualiza preferência de tamanho de fonte"""
    try:
        data = json.loads(request.body)
        font_size = data.get('font_size', 'medium')
        
        if font_size not in ['small', 'medium', 'large']:
            return JsonResponse({'success': False, 'error': 'Tamanho inválido'}, status=400)
        
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.font_size = font_size
        profile.save()
        
        return JsonResponse({'success': True, 'font_size': font_size})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)