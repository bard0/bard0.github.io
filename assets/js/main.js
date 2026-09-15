(() => {
  const root = document.documentElement;
  const themeBtn = document.querySelector('[data-theme-toggle]');
  const menuBtn = document.querySelector('[data-menu-toggle]');
  const navLinks = document.querySelector('.nav-links');

  const stored = localStorage.getItem('vg-theme');
  if (stored === 'light' || stored === 'dark') {
    root.dataset.theme = stored;
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    root.dataset.theme = 'dark';
  }

  const updateThemeLabel = () => {
    if (!themeBtn) return;
    const isDark = root.dataset.theme === 'dark';
    themeBtn.textContent = isDark ? '☀' : '☾';
    themeBtn.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
  };
  updateThemeLabel();

  themeBtn?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('vg-theme', root.dataset.theme);
    updateThemeLabel();
  });

  menuBtn?.addEventListener('click', () => {
    const open = navLinks?.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', String(Boolean(open)));
  });

  navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    menuBtn?.setAttribute('aria-expanded', 'false');
  }));
})();
