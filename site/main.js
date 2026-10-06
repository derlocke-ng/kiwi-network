// Kiwi Network homepage: theme toggle, mobile menu, copy buttons.
(function () {
  var root = document.documentElement;
  var KEY = 'kiwi-theme';

  function systemDark() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function current() {
    var t = root.getAttribute('data-theme');
    return t ? t : (systemDark() ? 'dark' : 'light');
  }

  var themeBtn = document.querySelector('.js-theme');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
    });
  }

  var nav = document.getElementById('nav');
  var menuBtn = document.querySelector('.js-menu');
  function setMenu(open) {
    if (!nav || !menuBtn) return;
    nav.classList.toggle('is-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      setMenu(!nav.classList.contains('is-open'));
    });
  }
  if (nav) {
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') setMenu(false);
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setMenu(false);
  });

  Array.prototype.forEach.call(document.querySelectorAll('.js-copy'), function (btn) {
    btn.addEventListener('click', function () {
      var el = document.getElementById(btn.getAttribute('data-copy'));
      if (!el) return;
      var text = el.textContent;
      var done = function () {
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1500);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var r = document.createRange();
        r.selectNodeContents(el);
        var s = window.getSelection();
        s.removeAllRanges();
        s.addRange(r);
      }
    });
  });
})();
