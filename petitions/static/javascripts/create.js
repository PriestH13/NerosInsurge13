// Update
document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('input[type="file"][name="image"]');
    const preview = document.getElementById('image-preview');

    if (input) {
      input.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
          };
          reader.readAsDataURL(file);
        }
      });
    }
  });



// Form
    document.addEventListener('DOMContentLoaded', function () {
        const input = document.querySelector('input[type="file"][name="image"]');
        const preview = document.getElementById('image-preview');
        const fileLabel = document.querySelector('.file-upload-label');

        input.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    fileLabel.innerHTML = `<i class="fas fa-check"></i> ${file.name}`;
                };
                reader.readAsDataURL(file);
            }
        });
    });



document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('location');
  const suggestions = document.getElementById('location-suggestions');

  function clearSuggestions() {
    suggestions.innerHTML = '';
    suggestions.style.display = 'none';
  }

  function showSuggestions(features) {
    suggestions.innerHTML = '';
    if (features.length === 0) {
      clearSuggestions();
      return;
    }
    features.forEach(feature => {
      const li = document.createElement('li');
      li.textContent = feature.properties.display_name || feature.properties.label;
      li.tabIndex = 0;
      li.addEventListener('click', () => {
        input.value = li.textContent;
        clearSuggestions();
      });
      suggestions.appendChild(li);
    });
    suggestions.style.display = 'block';
  }

  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  const fetchSuggestions = debounce(() => {
    const query = input.value.trim();
    if (query.length < 3) {
      clearSuggestions();
      return;
    }
fetch(`https://nominatim.openstreetmap.org/search?format=geojson&q=${encodeURIComponent(query)}&limit=5`)
      .then(res => res.json())
      .then(data => {
        if (data.features) {
          showSuggestions(data.features);
        } else {
          clearSuggestions();
        }
      })
      .catch(() => clearSuggestions());
  }, 300);

  input.addEventListener('input', fetchSuggestions);

  // Nascondo se click fuori
  document.addEventListener('click', (e) => {
    if (!suggestions.contains(e.target) && e.target !== input) {
      clearSuggestions();
    }
  });
});


document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('category-search');
  const select = document.querySelector('select[name="category"]');
  const suggestions = document.getElementById('category-suggestions');

  // Carico opzioni select in un array {value, label}
  const options = Array.from(select.options).map(opt => ({
    value: opt.value,
    label: opt.textContent.trim()
  }));

  function clearSuggestions() {
    suggestions.innerHTML = '';
    suggestions.style.display = 'none';
    input.setAttribute('aria-expanded', 'false');
  }

  function showSuggestions(filtered) {
    suggestions.innerHTML = '';
    if (filtered.length === 0) {
      clearSuggestions();
      return;
    }
    filtered.forEach(opt => {
      const li = document.createElement('li');
      li.textContent = opt.label;
      li.tabIndex = 0;
      li.setAttribute('role', 'option');
      li.addEventListener('click', () => {
        input.value = opt.label;
        select.value = opt.value;
        clearSuggestions();
      });
      li.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          li.click();
        }
      });
      suggestions.appendChild(li);
    });
    suggestions.style.display = 'block';
    input.setAttribute('aria-expanded', 'true');
  }

  input.addEventListener('input', () => {
    const val = input.value.toLowerCase();
    if (val.length < 1) {
      clearSuggestions();
      select.value = ''; // reset
      return;
    }
    const filtered = options.filter(opt => opt.label.toLowerCase().includes(val));
    showSuggestions(filtered);
  });

  // Se l’utente scrive ma poi esce, sincronizzo il valore con select se possibile
  input.addEventListener('blur', () => {
    setTimeout(() => {
      const match = options.find(opt => opt.label.toLowerCase() === input.value.trim().toLowerCase());
      if (match) {
        select.value = match.value;
      } else {
        select.value = '';
        input.value = '';
      }
      clearSuggestions();
    }, 150); // delay per click su suggerimento
  });

  // Inizializzo input con valore select se presente
  if (select.value) {
    const initOption = options.find(opt => opt.value === select.value);
    if (initOption) input.value = initOption.label;
  }
});


document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('tags-input');
  const suggestions = document.getElementById('tags-suggestions');

  // Lista tag esempio, da modificare con dati reali o API
  const availableTags = [
    'ambiente', 'diritti', 'cultura', 'educazione', 'salute', 'sicurezza', 'lavoro', 'tecnologia'
  ];

  function getLastTag(text) {
    const parts = text.split(',');
    return parts[parts.length - 1].trim().toLowerCase();
  }

  function clearSuggestions() {
    suggestions.innerHTML = '';
    suggestions.style.display = 'none';
    input.setAttribute('aria-expanded', 'false');
  }

  function showSuggestions(filtered) {
    suggestions.innerHTML = '';
    if (filtered.length === 0) {
      clearSuggestions();
      return;
    }
    filtered.forEach(tag => {
      const li = document.createElement('li');
      li.textContent = tag;
      li.tabIndex = 0;
      li.setAttribute('role', 'option');
      li.addEventListener('click', () => {
        let currentTags = input.value.split(',');
        currentTags[currentTags.length - 1] = tag;
        input.value = currentTags.map(t => t.trim()).filter(t => t.length > 0).join(', ') + ', ';
        clearSuggestions();
        input.focus();
      });
      li.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          li.click();
        }
      });
      suggestions.appendChild(li);
    });
    suggestions.style.display = 'block';
    input.setAttribute('aria-expanded', 'true');
  }

  input.addEventListener('input', () => {
    const lastTag = getLastTag(input.value);
    if (lastTag.length < 1) {
      clearSuggestions();
      return;
    }
    const filtered = availableTags.filter(tag => tag.toLowerCase().includes(lastTag));
    showSuggestions(filtered);
  });

  input.addEventListener('blur', () => {
    setTimeout(() => {
      clearSuggestions();
    }, 150);
  });
});


document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.getElementById('petitionsWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const cardWidth = 320; // Larghezza di una card (inclusi margini, adattala)
    let scrollAmount = 0;

    // Abilita/disabilita i pulsanti in base al contenuto
    function updateButtons() {
        prevBtn.disabled = scrollAmount <= 0;
        nextBtn.disabled = scrollAmount >= wrapper.scrollWidth - wrapper.clientWidth;
    }

    // Scorri a destra
    nextBtn.addEventListener('click', () => {
        scrollAmount += cardWidth;
        if (scrollAmount > wrapper.scrollWidth - wrapper.clientWidth) {
            scrollAmount = wrapper.scrollWidth - wrapper.clientWidth;
        }
        wrapper.scrollTo({ left: scrollAmount, behavior: 'smooth' });
        updateButtons();
    });

    // Scorri a sinistra
    prevBtn.addEventListener('click', () => {
        scrollAmount -= cardWidth;
        if (scrollAmount < 0) {
            scrollAmount = 0;
        }
        wrapper.scrollTo({ left: scrollAmount, behavior: 'smooth' });
        updateButtons();
    });

    // Inizializza lo stato dei pulsanti
    updateButtons();

    // Aggiorna i pulsanti quando la finestra viene ridimensionata
    window.addEventListener('resize', updateButtons);
});