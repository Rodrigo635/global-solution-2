// Configurar CSRF token para requisições AJAX
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

// Função para curtir/descurtir
function toggleLike(postId) {
    fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const likeIcon = document.getElementById(`like-icon-${postId}`);
        const likeCount = document.getElementById(`like-count-${postId}`);
        const likeBtn = document.querySelector(`button[data-post-id="${postId}"]`);
        
        if (data.liked) {
            likeIcon.classList.remove('bi-heart');
            likeIcon.classList.add('bi-heart-fill');
            likeBtn.classList.remove('btn-outline-danger');
            likeBtn.classList.add('btn-danger');
        } else {
            likeIcon.classList.remove('bi-heart-fill');
            likeIcon.classList.add('bi-heart');
            likeBtn.classList.remove('btn-danger');
            likeBtn.classList.add('btn-outline-danger');
        }
        
        likeCount.textContent = data.total_likes;
    })
    .catch(error => console.error('Erro:', error));
}