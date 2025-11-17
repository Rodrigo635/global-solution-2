// Controle de navegação entre seções dos amigos
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('.list-group-item');
    const sections = document.querySelectorAll('.content-section');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active de todos os links
            links.forEach(l => l.classList.remove('active'));
            
            // Adiciona active ao link clicado
            this.classList.add('active');
            
            // Esconde todas as seções
            sections.forEach(s => s.classList.remove('active'));
            
            // Mostra a seção correspondente
            const targetId = this.getAttribute('href').substring(1);
            document.getElementById(targetId).classList.add('active');
        });
    });
});

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

// Abrir modal de busca
function openSearchModal() {
    const modal = new bootstrap.Modal(document.getElementById('searchModal'));
    modal.show();
    
    // Limpar busca anterior
    document.getElementById('searchInput').value = '';
    document.getElementById('searchResults').innerHTML = `
        <div class="text-center text-muted py-3">
            <i class="bi bi-search" style="font-size: 2rem;"></i>
            <p class="mt-2 mb-0">Digite para buscar usuários</p>
        </div>
    `;
}

// Buscar usuários com debounce
let searchTimeout;
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                document.getElementById('searchResults').innerHTML = `
                    <div class="text-center text-muted py-3">
                        <i class="bi bi-search" style="font-size: 2rem;"></i>
                        <p class="mt-2 mb-0">Digite para buscar usuários</p>
                    </div>
                `;
                return;
            }
            
            searchTimeout = setTimeout(() => searchUsers(query), 500);
        });
    }
});

// Função de busca
async function searchUsers(query) {
    try {
        const response = await fetch(`/api/friends/search/?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        const resultsDiv = document.getElementById('searchResults');
        
        if (data.users.length === 0) {
            resultsDiv.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-person-x" style="font-size: 2rem;"></i>
                    <p class="mt-2 mb-0">Nenhum usuário encontrado</p>
                </div>
            `;
            return;
        }
        
        resultsDiv.innerHTML = data.users.map(user => {
            let buttonHtml = '';
            
            if (user.status === 'friend') {
                buttonHtml = '<span class="badge bg-success"><i class="bi bi-check-lg me-1"></i>Amigos</span>';
            } else if (user.status === 'sent') {
                buttonHtml = `<button class="btn btn-sm btn-outline-secondary" onclick="cancelRequest(${user.request_id})">Cancelar</button>`;
            } else if (user.status === 'received') {
                buttonHtml = `<button class="btn btn-sm btn-success" onclick="acceptRequest(${user.request_id})">Aceitar</button>`;
            } else {
                buttonHtml = `<button class="btn btn-sm btn-primary" onclick="sendRequest(${user.id})"><i class="bi bi-person-plus me-1"></i>Adicionar</button>`;
            }
            
            const avatar = user.avatar 
                ? `<img src="${user.avatar}" alt="avatar" class="rounded-2" style="width:50px; height:50px; object-fit:cover;">`
                : `<div class="rounded-2 bg-primary text-white d-flex align-items-center justify-content-center" style="width:50px; height:50px;"><i class="bi bi-person-fill"></i></div>`;
            
            return `
                <div class="search-result-item p-3 mb-2 border rounded">
                    <div class="d-flex align-items-center gap-3">
                        ${avatar}
                        <div class="flex-grow-1">
                            <div class="fw-semibold">${user.full_name}</div>
                            <div class="text-muted small">@${user.username}</div>
                        </div>
                        ${buttonHtml}
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        showToast('error', 'Erro ao buscar usuários');
    }
}

// Enviar solicitação de amizade
async function sendRequest(userId) {
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
            showToast('success', data.message);
            // Recarregar a busca
            const query = document.getElementById('searchInput').value;
            searchUsers(query);
        } else {
            showToast('error', data.error);
        }
    } catch (error) {
        console.error('Erro ao enviar solicitação:', error);
        showToast('error', 'Erro ao enviar solicitação');
    }
}

// Aceitar solicitação
async function acceptRequest(requestId) {
    try {
        const response = await fetch(`/api/friends/request/accept/${requestId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('success', data.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('error', data.error);
        }
    } catch (error) {
        console.error('Erro ao aceitar solicitação:', error);
        showToast('error', 'Erro ao aceitar solicitação');
    }
}

// Rejeitar solicitação
async function rejectRequest(requestId) {
    try {
        const response = await fetch(`/api/friends/request/reject/${requestId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('success', data.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('error', data.error);
        }
    } catch (error) {
        console.error('Erro ao rejeitar solicitação:', error);
        showToast('error', 'Erro ao rejeitar solicitação');
    }
}

// Cancelar solicitação enviada
async function cancelRequest(requestId) {
    try {
        const response = await fetch(`/api/friends/request/cancel/${requestId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('success', data.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('error', data.error);
        }
    } catch (error) {
        console.error('Erro ao cancelar solicitação:', error);
        showToast('error', 'Erro ao cancelar solicitação');
    }
}

// Remover amigo
async function removeFriend(userId, friendName) {
    if (!confirm(`Deseja realmente remover ${friendName} dos seus amigos?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/friends/remove/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('success', data.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('error', data.error);
        }
    } catch (error) {
        console.error('Erro ao remover amigo:', error);
        showToast('error', 'Erro ao remover amigo');
    }
}

// Função auxiliar para mostrar toast
function showToast(type, message) {
    // Usar o sistema de toast existente
    if (window.createToast) {
        window.createToast(message, type);
    } else {
        alert(message);
    }
}