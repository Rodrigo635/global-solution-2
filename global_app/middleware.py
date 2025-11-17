from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from datetime import timedelta

class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware para atualizar o timestamp de última atividade do usuário.
    Atualiza apenas a cada 2 minutos para evitar muitas queries ao banco.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Verificar se o usuário tem profile
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                
                # Atualizar apenas se a última atividade foi há mais de 2 minutos
                # Isso reduz a quantidade de writes no banco de dados
                time_threshold = timezone.now() - timedelta(minutes=2)
                
                if not profile.last_activity or profile.last_activity < time_threshold:
                    profile.update_last_activity()
        
        return None