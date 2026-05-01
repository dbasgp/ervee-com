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

// ========== Contact form ==========
// Form submits to FormSubmit (formsubmit.co) → dba@dba.sg with cc to dba@dba.hk.
// Just disable the submit button to prevent double-submits; let the form post normally.
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', () => {
    const btn = contactForm.querySelector('button[type="submit"]');
    if (btn) {
      btn.textContent = 'Sending…';
      btn.disabled = true;
    }
  });
}

// Show a confirmation banner if FormSubmit redirected back with ?sent=1
if (location.search.includes('sent=1')) {
  const banner = document.createElement('div');
  banner.style.cssText = 'position:fixed;top:80px;left:50%;transform:translateX(-50%);background:#22c55e;color:#fff;padding:14px 24px;border-radius:100px;font-weight:600;z-index:1000;box-shadow:0 8px 24px rgba(0,0,0,.15);max-width:90vw;text-align:center;';
  banner.textContent = '✓ Enquiry received — we will reply within one business day.';
  document.body.appendChild(banner);
  setTimeout(() => banner.remove(), 8000);
  history.replaceState({}, '', location.pathname + location.hash);
}
