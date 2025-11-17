from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),

    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='my_profile'),
    path('profile/<str:username>/', profile, name='public_profile'),
    path('friends/', friends, name='friends'),
    path('work_ai/', work_ai, name='work_ai'),

    path('feed/', feed, name='feed'),
    path('calls/', calls, name='calls'),
    path('chat/', chat, name='chat'),
    
    # Rota para curtir/descurtir posts
    path('post/<int:post_id>/like/', toggle_like, name='toggle_like'),
    
    # Rotas para configurações de perfil
    path('api/update-dark-mode/', update_dark_mode, name='update_dark_mode'),
    path('api/update-vlibras/', update_vlibras, name='update_vlibras'),
    path('api/update-font-size/', update_font_size, name='update_font_size'),
    
    # Rotas para amizades
    path('api/friends/search/', search_users, name='search_users'),
    path('api/friends/request/send/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('api/friends/request/accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('api/friends/request/reject/<int:request_id>/', reject_friend_request, name='reject_friend_request'),
    path('api/friends/request/cancel/<int:request_id>/', cancel_friend_request, name='cancel_friend_request'),
    path('api/friends/remove/<int:user_id>/', remove_friend, name='remove_friend'),
]