document.addEventListener('DOMContentLoaded', function () {
  const btnVideo = document.getElementById('btn-video');
  const searchCard = document.getElementById('search-card');
  const chatUrl = searchCard?.dataset.chatUrl || '/chat/';

  function searchingHtml() {
    return `
      <div class="text-center py-5">
        <h3>Buscando chamada</h3>
        <p class="small text-muted mb-3">Aguarde...</p>
        <div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>
      </div>
    `;
  }

  function startSearch() {
    searchCard.innerHTML = searchingHtml();
    setTimeout(() => {
      window.location.href = chatUrl;
    }, 5000);
  }

  if (btnVideo) btnVideo.addEventListener('click', startSearch);
});
