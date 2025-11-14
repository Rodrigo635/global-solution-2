from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),

    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='my_profile'),
    path('profile/<str:username>/', profile, name='public_profile'),

    path('feed/', feed, name='feed'),
    path('calls/', calls, name='calls'),
    path('chat/', chat, name='chat'),
    
    # Rota para curtir/descurtir posts
    path('post/<int:post_id>/like/', toggle_like, name='toggle_like'),
    
    # Rotas para configurações de perfil
    path('api/update-dark-mode/', update_dark_mode, name='update_dark_mode'),
    path('api/update-vlibras/', update_vlibras, name='update_vlibras'),
    path('api/update-font-size/', update_font_size, name='update_font_size'),
]