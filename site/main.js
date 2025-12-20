// Kiwi Network Landing Page JS

(function() {
  const root = document.documentElement;
  const storageKey = 'kiwi-network-theme';

  // Theme toggle
  function getPreferredTheme() {
    const saved = localStorage.getItem(storageKey);
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.removeAttribute('data-theme');
    }
  }

  applyTheme(getPreferredTheme());

  const themeToggle = document.querySelector('.js-theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(storageKey, next);
      applyTheme(next);
    });
  }

  // Mobile drawer
  const drawer = document.getElementById('drawer');
  const scrim = document.querySelector('.drawer-scrim');
  const menuToggle = document.querySelector('.js-menu-toggle');
  const closeButtons = document.querySelectorAll('.js-drawer-close');

  function setDrawerOpen(open) {
    if (!drawer) return;
    drawer.setAttribute('data-open', open ? 'true' : 'false');
    drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (scrim) scrim.hidden = !open;
    document.body.style.overflow = open ? 'hidden' : '';
  }

  if (menuToggle) {
    menuToggle.addEventListener('click', () => setDrawerOpen(true));
  }

  closeButtons.forEach(btn => {
    btn.addEventListener('click', () => setDrawerOpen(false));
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Close drawer if open
        setDrawerOpen(false);
      }
    });
  });
})();
