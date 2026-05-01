// ========== Mobile nav ==========
function toggleNav() {
  document.getElementById('mobileNav').classList.toggle('open');
}

// ========== Scroll-triggered reveals ==========
const revealEls = document.querySelectorAll('.reveal, .reveal-img');
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      revealObs.unobserve(e.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
revealEls.forEach((el) => revealObs.observe(el));

// ========== Sticky tech-stage image switching ==========
const techSteps = document.querySelectorAll('.tech-step');
const techImgs = document.querySelectorAll('.tech-img');
if (techSteps.length && techImgs.length) {
  const techObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        const idx = e.target.getAttribute('data-step');
        techImgs.forEach((img) => img.classList.toggle('active', img.getAttribute('data-tech') === idx));
      }
    });
  }, { rootMargin: '-40% 0px -40% 0px', threshold: 0 });
  techSteps.forEach((s) => techObs.observe(s));
}

// ========== Nav background on scroll ==========
const navEl = document.getElementById('nav');
const onScroll = () => {
  if (window.scrollY > 12) {
    navEl.style.background = 'rgba(255,255,255,0.92)';
    navEl.style.borderBottomColor = 'rgba(0,0,0,0.08)';
  } else {
    navEl.style.background = 'rgba(255,255,255,0.72)';
    navEl.style.borderBottomColor = 'rgba(0,0,0,0.06)';
  }
};
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// ========== Hero parallax ==========
const heroProduct = document.querySelector('.hero-product img');
if (heroProduct) {
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight) {
      const scale = 1 + Math.min(y / 4000, 0.05);
      const translate = Math.min(y * 0.15, 80);
      heroProduct.style.transform = `translateY(${translate}px) scale(${scale})`;
    }
  }, { passive: true });
}

// ========== Quote form submission ==========
const quoteForm = document.getElementById('quoteForm');
if (quoteForm) {
  quoteForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = quoteForm.querySelector('button[type="submit"]');
    btn.textContent = 'Sent — we will be in touch';
    btn.style.background = '#1d1d1f';
    btn.disabled = true;
    const fineprint = quoteForm.querySelector('.form-fineprint');
    if (fineprint) fineprint.textContent = 'Thanks — your enquiry has been received.';
  });
}
