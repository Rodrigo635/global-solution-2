// Obter CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Função para curtir/descurtir posts
async function toggleLike(postId) {
    try {
        const response = await fetch(`/post/${postId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Erro na requisição');
        }

        const data = await response.json();
        
        // Atualizar o ícone do coração
        const icon = document.getElementById(`like-icon-${postId}`);
        const button = icon.closest('button');
        
        if (data.liked) {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
            button.classList.remove('btn-outline-danger');
            button.classList.add('btn-danger');
        } else {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
            button.classList.remove('btn-danger');
            button.classList.add('btn-outline-danger');
        }
        
        // Atualizar o contador
        document.getElementById(`like-count-${postId}`).textContent = data.total_likes;
        
    } catch (error) {
        console.error('Erro ao curtir/descurtir:', error);
        showToast('error', 'Erro ao processar sua curtida. Tente novamente.');
    }
}

// Função para enviar solicitação de amizade
async function sendFriendRequest(userId, userName, buttonElement) {
    // Desabilitar botão para evitar cliques múltiplos
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Enviando...';
    
    try {
        const response = await fetch(`/api/friends/request/send/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar mensagem de sucesso
            showToast('success', `Solicitação enviada para ${userName}!`);
            
            // Atualizar o botão para mostrar que foi enviado
            buttonElement.classList.remove('btn-outline-primary');
            buttonElement.classList.add('btn-secondary');
            buttonElement.innerHTML = '<i class="bi bi-check-lg me-1"></i>Enviado';
            buttonElement.disabled = true;
            
            // Opcional: remover o onclick para evitar cliques futuros
            buttonElement.onclick = null;
            
        } else {
            // Mostrar mensagem de erro
            showToast('error', data.error || 'Erro ao enviar solicitação');
            
            // Reabilitar botão
            buttonElement.disabled = false;
            buttonElement.innerHTML = '<i class="bi bi-plus me-1"></i>Adicionar';
        }
        
    } catch (error) {
        console.error('Erro ao enviar solicitação:', error);
        showToast('error', 'Erro ao enviar solicitação. Tente novamente.');
        
        // Reabilitar botão
        buttonElement.disabled = false;
        buttonElement.innerHTML = '<i class="bi bi-plus me-1"></i>Adicionar';
    }
}

// Função auxiliar para mostrar toast (usa o sistema existente)
function showToast(type, message) {
    // Usar o sistema de toast existente do projeto
    if (window.createToast) {
        window.createToast(message, type);
    } else {
        // Fallback caso o sistema de toast não esteja disponível
        alert(message);
    }
}

// Carregar status de amizade ao carregar a página (opcional - melhoria futura)
document.addEventListener('DOMContentLoaded', function() {
    // Aqui você pode adicionar lógica para verificar o status de amizade
    // de cada usuário sugerido e atualizar os botões de acordo
    checkFriendshipStatus();
});

// Função para verificar status de amizade dos usuários sugeridos
async function checkFriendshipStatus() {
    const addButtons = document.querySelectorAll('.add-friend-btn');
    
    for (const button of addButtons) {
        const userId = button.getAttribute('data-user-id');
        
        try {
            // Buscar o usuário para verificar status
            const response = await fetch(`/api/friends/search/?q=id:${userId}`);
            const data = await response.json();
            
            if (data.users && data.users.length > 0) {
                const user = data.users[0];
                
                // Atualizar botão baseado no status
                if (user.status === 'friend') {
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-success');
                    button.innerHTML = '<i class="bi bi-check-lg me-1"></i>Amigos';
                    button.disabled = true;
                    button.onclick = null;
                } else if (user.status === 'sent') {
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-secondary');
                    button.innerHTML = '<i class="bi bi-check-lg me-1"></i>Enviado';
                    button.disabled = true;
                    button.onclick = null;
                } else if (user.status === 'received') {
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-info');
                    button.innerHTML = '<i class="bi bi-envelope-check me-1"></i>Aceitar';
                    button.onclick = function() {
                        window.location.href = '/friends/#solicitacoes';
                    };
                }
            }
        } catch (error) {
            // Silenciosamente ignorar erros de verificação
            console.log('Não foi possível verificar status para usuário:', userId);
        }
    }
}