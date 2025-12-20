(function () {
  const storageKey = 'kiwi-network-theme';
  const root = document.documentElement;
  const button = document.getElementById('themeToggle');

  function apply(theme) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
      if (button) button.textContent = '☀️ Light';
      return;
    }

    root.removeAttribute('data-theme');
    if (button) button.textContent = '🌙 Dark';
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

  if (button) {
    button.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem(storageKey, next);
      apply(next);
    });
  }
})();
