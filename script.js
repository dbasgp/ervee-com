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
// AJAX-posts to a Make.com webhook. User stays on the page; we show a green
// confirmation banner on success.
function showFormBanner(message, ok = true) {
  const banner = document.createElement('div');
  banner.style.cssText = 'position:fixed;top:80px;left:50%;transform:translateX(-50%);background:' + (ok ? '#22c55e' : '#ef4444') + ';color:#fff;padding:14px 24px;border-radius:100px;font-weight:600;z-index:1000;box-shadow:0 8px 24px rgba(0,0,0,.15);max-width:90vw;text-align:center;';
  banner.textContent = message;
  document.body.appendChild(banner);
  setTimeout(() => banner.remove(), 8000);
}

const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    // Honeypot — if filled, silently drop
    const honey = contactForm.querySelector('[name="_honey"]');
    if (honey && honey.value) return;

    const btn = contactForm.querySelector('button[type="submit"]');
    const fineprint = contactForm.querySelector('.form-fineprint');
    const originalLabel = btn ? btn.textContent : '';
    if (btn) { btn.textContent = 'Sending…'; btn.disabled = true; }

    const data = new FormData(contactForm);
    try {
      const res = await fetch(contactForm.action, { method: 'POST', body: data });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      contactForm.reset();
      if (btn) { btn.textContent = '✓ Sent — thank you'; btn.style.background = '#22c55e'; }
      if (fineprint) fineprint.textContent = 'Enquiry received. We will reply within one business day.';
      showFormBanner('✓ Enquiry received — we will reply within one business day.');
    } catch (err) {
      if (btn) { btn.textContent = originalLabel || 'Send enquiry'; btn.disabled = false; }
      showFormBanner('Sorry — something went wrong. Please email dba@dba.sg directly.', false);
    }
  });
}
