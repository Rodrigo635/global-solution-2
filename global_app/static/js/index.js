// Smooth scroll
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Fechar os alertas automatico
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alertEl => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                bsAlert.close();
            } catch (err) {
                const btn = alertEl.querySelector('.btn-close');
                if (btn) btn.click();
            }
        });
    }, 5000);
});