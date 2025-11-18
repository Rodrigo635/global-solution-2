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
from .models import Post, Like, Profile, Friendship, FriendRequest, Opportunity, Application
from django.db.models import Q
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
    """View do perfil - renderiza template diferente para perfil próprio vs público"""
    
    # Se username não informado, mostra o perfil do usuário logado
    if username:
        # Ver o perfil público de outro usuário
        user = get_object_or_404(User, username=username)
        is_own_profile = (user == request.user)
    else:
        # Perfil próprio
        user = request.user
        is_own_profile = True

    profile = getattr(user, 'profile', None)
    
    # Criar perfil se não existir (apenas para o próprio usuário)
    if not profile and is_own_profile:
        profile = Profile.objects.create(user=user)
    
    # Se é o próprio perfil, renderiza o template de perfil próprio
    if is_own_profile:
        context = {'user': user, 'profile': profile}
        return render(request, 'pages/profile.html', context)
    
    # Se não é o próprio perfil, renderiza o template de perfil público
    # Verificar status de amizade
    is_friend = Friendship.objects.filter(user=request.user, friend=user).exists()
    
    # Verificar se existe solicitação pendente
    friend_request = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=user) | 
        Q(from_user=user, to_user=request.user),
        status='pending'
    ).first()
    
    friendship_status = 'none'
    friend_request_id = None
    
    if is_friend:
        friendship_status = 'friend'
    elif friend_request:
        if friend_request.from_user == request.user:
            friendship_status = 'request_sent'
        else:
            friendship_status = 'request_received'
        friend_request_id = friend_request.id
    
    # Buscar posts do usuário
    user_posts = Post.objects.filter(author=user).select_related('author', 'author__profile').prefetch_related('likes')[:10]
    
    # Adicionar informação se o usuário curtiu cada post
    for post in user_posts:
        post.user_has_liked = post.likes.filter(user=request.user).exists()
    
    # Contar amigos do usuário
    friends_count = Friendship.objects.filter(user=user).count()
    
    # Buscar amigos em comum
    user_friends = Friendship.objects.filter(user=user).values_list('friend_id', flat=True)
    my_friends = Friendship.objects.filter(user=request.user).values_list('friend_id', flat=True)
    mutual_friend_ids = set(user_friends).intersection(set(my_friends))
    mutual_friends = User.objects.filter(id__in=mutual_friend_ids).select_related('profile')[:10]
    
    context = {
        'user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'friendship_status': friendship_status,
        'friend_request_id': friend_request_id,
        'user_posts': user_posts,
        'user_posts_count': user_posts.count(),
        'friends_count': friends_count,
        'mutual_friends': mutual_friends,
    }
    
    return render(request, 'pages/public_profile.html', context)

@login_required
def feed(request):
    # Buscar usuários sugeridos excluindo:
    # - O próprio usuário
    # - Usuários que já são amigos
    # - Usuários com solicitação pendente
    
    # IDs dos amigos atuais
    friend_ids = Friendship.objects.filter(user=request.user).values_list('friend_id', flat=True)
    
    # IDs de usuários com solicitação pendente (enviada ou recebida)
    pending_request_ids = list(FriendRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='pending'
    ).values_list('to_user_id', 'from_user_id'))
    
    # Flatten a lista de tuplas e remover duplicatas
    pending_ids = set()
    for id_tuple in pending_request_ids:
        pending_ids.update(id_tuple)
    pending_ids.discard(request.user.id)  # Remover o próprio usuário se estiver
    
    # Buscar usuários que NÃO são amigos e NÃO têm solicitação pendente
    suggested_users = User.objects.exclude(
        id__in=list(friend_ids) + list(pending_ids) + [request.user.id]
    ).select_related('profile').order_by('?')[:5]
    
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

@login_required
def work_ai(request):
    return render(request, 'pages/work_ai.html')

@login_required
def friends(request):
    """View principal da página de amigos"""
    # Buscar todos os amigos do usuário
    friendships = Friendship.objects.filter(user=request.user).select_related('friend', 'friend__profile')
    friends_list = [f.friend for f in friendships]
    
    # Separar amigos online e offline baseado no status real
    online_friends = []
    offline_friends = []
    
    for friend in friends_list:
        # Verificar se o amigo tem profile e se está online
        if hasattr(friend, 'profile') and friend.profile and friend.profile.is_online():
            online_friends.append(friend)
        else:
            offline_friends.append(friend)
    
    # Buscar solicitações recebidas pendentes
    received_requests = FriendRequest.objects.filter(
        to_user=request.user, 
        status='pending'
    ).select_related('from_user', 'from_user__profile')
    
    # Buscar solicitações enviadas pendentes
    sent_requests = FriendRequest.objects.filter(
        from_user=request.user, 
        status='pending'
    ).select_related('to_user', 'to_user__profile')
    
    context = {
        'online_friends': online_friends,
        'offline_friends': offline_friends,
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    
    return render(request, 'pages/friends.html', context)


@login_required
@require_POST
def send_friend_request(request, user_id):
    """Envia uma solicitação de amizade"""
    try:
        to_user = get_object_or_404(User, id=user_id)
        
        # Verificar se não está tentando adicionar a si mesmo
        if to_user == request.user:
            return JsonResponse({'success': False, 'error': 'Você não pode adicionar a si mesmo'}, status=400)
        
        # Verificar se já são amigos
        if Friendship.objects.filter(user=request.user, friend=to_user).exists():
            return JsonResponse({'success': False, 'error': 'Vocês já são amigos'}, status=400)
        
        # Verificar se já existe uma solicitação pendente
        existing_request = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=to_user) | 
            Q(from_user=to_user, to_user=request.user),
            status='pending'
        ).first()
        
        if existing_request:
            return JsonResponse({'success': False, 'error': 'Já existe uma solicitação pendente'}, status=400)
        
        # Criar solicitação
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitação enviada com sucesso',
            'request_id': friend_request.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def accept_friend_request(request, request_id):
    """Aceita uma solicitação de amizade"""
    try:
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        
        if friend_request.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Esta solicitação já foi processada'}, status=400)
        
        # Aceitar solicitação (cria amizade bidirecional)
        friend_request.accept()
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitação aceita com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def reject_friend_request(request, request_id):
    """Rejeita uma solicitação de amizade"""
    try:
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        
        if friend_request.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Esta solicitação já foi processada'}, status=400)
        
        friend_request.reject()
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitação rejeitada'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def cancel_friend_request(request, request_id):
    """Cancela uma solicitação enviada"""
    try:
        friend_request = get_object_or_404(FriendRequest, id=request_id, from_user=request.user)
        
        if friend_request.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Esta solicitação já foi processada'}, status=400)
        
        friend_request.cancel()
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitação cancelada'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def remove_friend(request, user_id):
    """Remove um amigo"""
    try:
        friend = get_object_or_404(User, id=user_id)
        
        # Remover amizade bidirecional
        Friendship.objects.filter(user=request.user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=request.user).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Amigo removido com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def search_users(request):
    """Busca usuários para adicionar como amigos"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'users': []})
    
    # Buscar usuários excluindo o próprio usuário
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id).select_related('profile')[:10]
    
    # Verificar status de amizade para cada usuário
    results = []
    for user in users:
        # Verificar se já são amigos
        is_friend = Friendship.objects.filter(user=request.user, friend=user).exists()
        
        # Verificar se existe solicitação pendente
        pending_request = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=user) | 
            Q(from_user=user, to_user=request.user),
            status='pending'
        ).first()
        
        status = 'none'
        request_id = None
        
        if is_friend:
            status = 'friend'
        elif pending_request:
            if pending_request.from_user == request.user:
                status = 'sent'
                request_id = pending_request.id
            else:
                status = 'received'
                request_id = pending_request.id
        
        results.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'avatar': user.profile.avatar.url if user.profile and user.profile.avatar else None,
            'bio': user.profile.bio if user.profile else '',
            'status': status,
            'request_id': request_id
        })
    
    return JsonResponse({'users': results})

@login_required
def opportunities(request):
    """View principal da página de oportunidades"""
    # Filtros
    opportunity_type = request.GET.get('type', '')
    search_query = request.GET.get('q', '')
    
    # Buscar oportunidades abertas
    opportunities_list = Opportunity.objects.filter(status='open')
    
    # Aplicar filtros
    if opportunity_type:
        opportunities_list = opportunities_list.filter(type=opportunity_type)
    
    if search_query:
        opportunities_list = opportunities_list.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    opportunities_list = opportunities_list.order_by('-created_at')
    
    # Verificar quais oportunidades o usuário já se inscreveu
    user_applications = Application.objects.filter(user=request.user).values_list('opportunity_id', flat=True)
    
    for opp in opportunities_list:
        opp.user_applied = opp.id in user_applications
    
    # Buscar inscrições do usuário
    user_applications_list = Application.objects.filter(user=request.user).select_related('opportunity').order_by('-applied_at')
    
    context = {
        'opportunities': opportunities_list,
        'user_applications': user_applications_list,
        'current_type': opportunity_type,
        'search_query': search_query,
    }
    
    return render(request, 'pages/opportunities.html', context)

@login_required
def opportunity_detail(request, opportunity_id):
    """View de detalhes de uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    
    # Verificar se o usuário já se inscreveu
    user_application = Application.objects.filter(
        opportunity=opportunity,
        user=request.user
    ).first()
    
    context = {
        'opportunity': opportunity,
        'user_application': user_application,
    }
    
    return render(request, 'pages/opportunity_detail.html', context)

@login_required
@require_POST
def apply_opportunity(request, opportunity_id):
    """Inscrição em uma oportunidade"""
    try:
        opportunity = get_object_or_404(Opportunity, id=opportunity_id)
        
        # Verificar se a oportunidade está aberta
        if opportunity.status != 'open':
            return JsonResponse({'success': False, 'error': 'Esta oportunidade está fechada'}, status=400)
        
        # Verificar se já expirou
        if opportunity.is_expired():
            return JsonResponse({'success': False, 'error': 'O prazo de inscrição expirou'}, status=400)
        
        # Verificar se já se inscreveu
        if Application.objects.filter(opportunity=opportunity, user=request.user).exists():
            return JsonResponse({'success': False, 'error': 'Você já se inscreveu nesta oportunidade'}, status=400)
        
        # Pegar dados do formulário
        data = json.loads(request.body)
        cover_letter = data.get('cover_letter', '')
        
        # Criar inscrição
        application = Application.objects.create(
            opportunity=opportunity,
            user=request.user,
            cover_letter=cover_letter,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Inscrição realizada com sucesso!',
            'application_id': application.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def cancel_application(request, application_id):
    """Cancela uma inscrição"""
    try:
        application = get_object_or_404(Application, id=application_id, user=request.user)
        
        # Só pode cancelar se ainda estiver pendente
        if application.status != 'pending':
            return JsonResponse({'success': False, 'error': 'Não é possível cancelar esta inscrição'}, status=400)
        
        application.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Inscrição cancelada com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'pages/terms_of_use.html')