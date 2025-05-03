
  // Spinning loading logo
  document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', () => {
        document.getElementById('loadingSpinner').style.display = 'flex';
      });
    });
  });

