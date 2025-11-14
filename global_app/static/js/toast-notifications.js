/**
 * Sistema de Notificações Toast
 */

// Mapeamento de ícones por tipo de mensagem
const toastIcons = {
    success: 'bi-check-circle-fill',
    error: 'bi-x-circle-fill',
    danger: 'bi-exclamation-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill'
};

/**
 * Cria e exibe uma notificação toast
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo da mensagem (success, error, warning, info, danger)
 * @param {number} duration - Duração em ms (default: 5000)
 */
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Criar elemento do toast
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    // Definir ícone baseado no tipo
    const iconClass = toastIcons[type] || toastIcons.info;
    
    // Estrutura HTML do toast
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="bi ${iconClass}"></i>
        </div>
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="closeToast(this)">×</button>
        <div class="toast-progress"></div>
    `;
    
    // Adicionar ao container
    container.appendChild(toast);
    
    // Auto-remover após duração especificada
    setTimeout(() => {
        closeToast(toast.querySelector('.toast-close'));
    }, duration);
}

/**
 * Fecha um toast específico
 * @param {HTMLElement} closeButton - Botão de fechar clicado
 */
function closeToast(closeButton) {
    const toast = closeButton.closest('.toast-notification');
    if (!toast) return;
    
    // Adicionar classe de animação de saída
    toast.classList.add('hiding');
    
    // Remover do DOM após animação
    setTimeout(() => {
        toast.remove();
    }, 300);
}

/**
 * Converte mensagens do Django em toasts
 */
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('django-messages');
    
    if (messagesContainer) {
        const messages = messagesContainer.querySelectorAll('[data-message]');
        
        messages.forEach((msgElement, index) => {
            const message = msgElement.getAttribute('data-message');
            const tags = msgElement.getAttribute('data-tags') || 'info';
            
            // Delay progressivo para múltiplas mensagens
            setTimeout(() => {
                showToast(message, tags);
            }, index * 200);
        });
        
        // Remover container de mensagens após processar
        messagesContainer.remove();
    }
});

// Tornar funções globais para uso em outros scripts
window.showToast = showToast;
window.closeToast = closeToast;