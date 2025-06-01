document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('id_profile_picture');
  const preview = document.getElementById('preview-img');
  const placeholder = document.querySelector('.image-placeholder');
  const feedback = document.createElement('div');
  feedback.className = 'feedback-message';
  const previewContainer = document.querySelector('.image-preview');
  const maxFileSize = 5 * 1024 * 1024;

  if (!input || !preview || !placeholder || !previewContainer) {
    console.warn("Elementi necessari non trovati (input, preview, placeholder o container).");
    return;
  }

  previewContainer.appendChild(feedback);

  const resetPreview = () => {
    preview.src = '';
    preview.classList.add('hidden');
    placeholder.classList.remove('hidden');
    feedback.textContent = '';
    feedback.classList.remove('error');
    input.value = '';
  };

  resetPreview();

  //caricamento
  const triggerFileInput = () => {
    input.click();
  };

  preview.addEventListener('click', triggerFileInput);
  placeholder.addEventListener('click', triggerFileInput);
  placeholder.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      triggerFileInput();
    }
  });

  input.addEventListener('change', (event) => {
    const file = event.target.files[0];
    feedback.textContent = '';

    if (file) {
      if (!file.type.startsWith('image/')) {
        resetPreview();
        feedback.textContent = 'Seleziona un file immagine valido (es. JPG, PNG).';
        feedback.classList.add('error');
        return;
      }

      if (file.size > maxFileSize) {
        resetPreview();
        feedback.textContent = 'L\'immagine è troppo grande (massimo 5MB).';
        feedback.classList.add('error');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        preview.src = e.target.result;
        preview.classList.remove('hidden');
        placeholder.classList.add('hidden');
        feedback.textContent = 'Nuova immagine caricata!';
        feedback.classList.remove('error');
      };
      reader.onerror = () => {
        resetPreview();
        feedback.textContent = 'Errore durante il caricamento.';
        feedback.classList.add('error');
      };
      reader.readAsDataURL(file);
    } else {
      resetPreview();
    }
  });
});