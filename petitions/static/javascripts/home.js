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
document.addEventListener('DOMContentLoaded', function() {
    const wrapper = document.getElementById('petitionsWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    let isDragging = false;
    let startX;
    let scrollLeft;
    
    // Scroll manuale con bottoni
    nextBtn.addEventListener('click', () => {
        wrapper.scrollBy({ left: 320, behavior: 'smooth' });
    });
    
    prevBtn.addEventListener('click', () => {
        wrapper.scrollBy({ left: -320, behavior: 'smooth' });
    });
    
    // Drag per mobile/touch devices
    wrapper.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.pageX - wrapper.offsetLeft;
        scrollLeft = wrapper.scrollLeft;
        wrapper.style.cursor = 'grabbing';
        wrapper.style.scrollBehavior = 'auto';
    });
    
    wrapper.addEventListener('mouseleave', () => {
        if (isDragging) {
            isDragging = false;
            wrapper.style.cursor = 'grab';
        }
    });
    
    wrapper.addEventListener('mouseup', () => {
        isDragging = false;
        wrapper.style.cursor = 'grab';
        wrapper.style.scrollBehavior = 'smooth';
    });
    
    wrapper.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - wrapper.offsetLeft;
        const walk = (x - startX) * 2;
        wrapper.scrollLeft = scrollLeft - walk;
    });
    
    // Touch events per mobile
    wrapper.addEventListener('touchstart', (e) => {
        isDragging = true;
        startX = e.touches[0].pageX - wrapper.offsetLeft;
        scrollLeft = wrapper.scrollLeft;
        wrapper.style.scrollBehavior = 'auto';
    });
    
    wrapper.addEventListener('touchend', () => {
        isDragging = false;
        wrapper.style.scrollBehavior = 'smooth';
    });
    
    wrapper.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        const x = e.touches[0].pageX - wrapper.offsetLeft;
        const walk = (x - startX) * 2;
        wrapper.scrollLeft = scrollLeft - walk;
    });
    
    // Disabilita bottoni quando si raggiunge l'inizio/fine
    wrapper.addEventListener('scroll', () => {
        const maxScroll = wrapper.scrollWidth - wrapper.clientWidth;
        
        if (wrapper.scrollLeft <= 0) {
            prevBtn.disabled = true;
        } else {
            prevBtn.disabled = false;
        }
        
        if (wrapper.scrollLeft >= maxScroll) {
            nextBtn.disabled = true;
        } else {
            nextBtn.disabled = false;
        }
    });
    
    // Inizializza stato bottoni
    prevBtn.disabled = true;
});



