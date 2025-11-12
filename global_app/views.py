from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.urls import reverse
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth.models import User

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

def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Olá {user.first_name or user.username} — você entrou com sucesso.")
            return redirect(next_url or settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'pages/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Você saiu da conta.")
    return redirect('home')

@login_required
def profile_view(request, username=None):
    # Se username não informado, mostra o perfil do usuário logado
    if username:
        # Ver o perfil público
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = getattr(user, 'profile', None)
    context = {'user': user, 'profile': profile}
    
    return render(request, 'pages/profile.html', context)

