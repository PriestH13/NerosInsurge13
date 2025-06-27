// ---Ricerca per il per non aggiornare la pagina---
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form');
    const resultsDiv = document.getElementById('petition-results');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const params = new URLSearchParams(formData).toString();

        fetch(window.location.pathname + '?' + params, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            resultsDiv.innerHTML = html;
        })
        .catch(err => console.error('Errore caricamento risultati:', err));
    });
});

document.addEventListener('DOMContentLoaded', () => {
  const marquee = document.querySelector('.marquee');
  const content = marquee.querySelector('.marquee-content');

  // Clona il contenuto per farlo scorrere in loop continuo
  const clone = content.cloneNode(true);
  marquee.appendChild(clone);
});
