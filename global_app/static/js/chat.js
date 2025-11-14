  // Controle de câmera
  const cameraBtn = document.getElementById('cameraBtn');
  let cameraActive = true;

  cameraBtn.addEventListener('click', () => {
    cameraActive = !cameraActive;
    cameraBtn.classList.toggle('active');
    
    if (cameraActive) {
      cameraBtn.innerHTML = '<i class="bi bi-camera-video-fill"></i>';
    } else {
      cameraBtn.innerHTML = '<i class="bi bi-camera-video-off-fill"></i>';
    }
  });

  // Controle de microfone
  const micBtn = document.getElementById('micBtn');
  let micActive = true;

  micBtn.addEventListener('click', () => {
    micActive = !micActive;
    micBtn.classList.toggle('active');
    
    if (micActive) {
      micBtn.innerHTML = '<i class="bi bi-mic-fill"></i>';
    } else {
      micBtn.innerHTML = '<i class="bi bi-mic-mute-fill"></i>';
    }
  });

  // Botão de desconectar
  const disconnectBtn = document.getElementById('disconnectBtn');
  disconnectBtn.addEventListener('click', () => {
    if (confirm('Deseja realmente desconectar da chamada?')) {
      window.location.href = '/calls/';
    }
  });
