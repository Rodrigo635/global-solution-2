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

// Variável global para armazenar o ID da oportunidade atual
let currentOpportunityId = null;

// Abrir modal de inscrição rápida
function quickApply(opportunityId, opportunityTitle) {
    currentOpportunityId = opportunityId;
    document.getElementById('modalOpportunityTitle').textContent = opportunityTitle;
    document.getElementById('coverLetter').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('applyModal'));
    modal.show();
}

// Confirmar inscrição
document.addEventListener('DOMContentLoaded', function() {
    const confirmBtn = document.getElementById('confirmApplyBtn');
    
    if (confirmBtn) {
        confirmBtn.addEventListener('click', async function() {
            const coverLetter = document.getElementById('coverLetter').value.trim();
            
            // Desabilitar botão durante o envio
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Enviando...';
            
            try {
                const response = await fetch(`/api/opportunities/apply/${currentOpportunityId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        cover_letter: coverLetter
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Fechar modal
                    bootstrap.Modal.getInstance(document.getElementById('applyModal')).hide();
                    
                    // Mostrar mensagem de sucesso
                    showToast('success', data.message);
                    
                    // Recarregar página após 1 segundo
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('error', data.error || 'Erro ao enviar inscrição');
                    
                    // Reabilitar botão
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Confirmar Inscrição';
                }
                
            } catch (error) {
                console.error('Erro:', error);
                showToast('error', 'Erro ao enviar inscrição. Tente novamente.');
                
                // Reabilitar botão
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Confirmar Inscrição';
            }
        });
    }
});

// Cancelar inscrição
async function cancelApplication(applicationId) {
    if (!confirm('Deseja realmente cancelar esta inscrição?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/opportunities/cancel/${applicationId}/`, {
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
        console.error('Erro:', error);
        showToast('error', 'Erro ao cancelar inscrição');
    }
}

// Função auxiliar para mostrar toast
function showToast(type, message) {
    if (window.createToast) {
        window.createToast(message, type);
    } else {
        alert(message);
    }
}