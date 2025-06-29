window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});
// ---------------------------------
// petitions-slider.js
document.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.getElementById("petitionsWrapper");
  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  const scrollAmount = 320;

  if (!wrapper || !nextBtn || !prevBtn) return;

  function scrollNext() {
    wrapper.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  }

  function scrollPrev() {
    wrapper.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  }

  nextBtn.addEventListener("click", scrollNext);
  prevBtn.addEventListener("click", scrollPrev);

  // Auto scroll ogni 5 secondi
  let autoScroll = setInterval(() => {
    if (wrapper.scrollLeft + wrapper.clientWidth >= wrapper.scrollWidth - 5) {
      wrapper.scrollTo({ left: 0, behavior: 'smooth' }); // Torna all'inizio
    } else {
      scrollNext();
    }
  }, 5000);

  // Pausa auto scroll se utente interagisce
  wrapper.addEventListener("mouseenter", () => clearInterval(autoScroll));
  wrapper.addEventListener("mouseleave", () => {
    autoScroll = setInterval(() => {
      if (wrapper.scrollLeft + wrapper.clientWidth >= wrapper.scrollWidth - 5) {
        wrapper.scrollTo({ left: 0, behavior: 'smooth' });
      } else {
        scrollNext();
      }
    }, 5000);
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('nav-toggle');
  const mobileNav = document.querySelector('.mobile-nav');

  mobileNav.querySelectorAll('a, button').forEach(el => {
    el.addEventListener('click', () => {
      // Chiudi menu al click
      navToggle.checked = false;
    });
  });
});
