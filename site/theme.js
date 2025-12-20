(function () {
  const storageKey = 'kiwi-network-theme';
  const root = document.documentElement;
  const themeButtons = Array.from(document.querySelectorAll('.js-theme-toggle'));

  const drawer = document.getElementById('drawer');
  const scrim = document.querySelector('.scrim');
  const openBtn = document.querySelector('.js-drawer-open');
  const closeButtons = Array.from(document.querySelectorAll('.js-drawer-close'));

  function apply(theme) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
      for (const btn of themeButtons) btn.textContent = '☀️ Light';
      return;
    }

    root.removeAttribute('data-theme');
    for (const btn of themeButtons) btn.textContent = '🌙 Dark';
  }

  function getPreferred() {
    const saved = localStorage.getItem(storageKey);
    if (saved === 'dark' || saved === 'light') return saved;

    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  const initial = getPreferred();
  apply(initial);

  for (const btn of themeButtons) {
    btn.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem(storageKey, next);
      apply(next);
    });
  }

  function setDrawerOpen(isOpen) {
    if (!drawer) return;
    drawer.setAttribute('data-open', isOpen ? 'true' : 'false');
    drawer.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
    if (openBtn) openBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    if (scrim) {
      scrim.hidden = !isOpen;
    }
  }

  if (openBtn) {
    openBtn.addEventListener('click', () => setDrawerOpen(true));
  }

  for (const btn of closeButtons) {
    btn.addEventListener('click', () => setDrawerOpen(false));
  }

  if (drawer) {
    drawer.addEventListener('click', (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      if (target.closest('a')) setDrawerOpen(false);
    });
  }
})();
