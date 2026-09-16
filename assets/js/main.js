(() => {
  const root = document.documentElement;
  const themeBtn = document.querySelector('[data-theme-toggle]');
  const menuBtn = document.querySelector('[data-menu-toggle]');
  const navLinks = document.querySelector('.nav-links');
  const isRu = (root.lang || '').toLowerCase().startsWith('ru');
  const heroPhoto = document.querySelector('.hero-photo');

  if (heroPhoto) {
    const assetBase = isRu ? '../assets/img/hero-hq/' : 'assets/img/hero-hq/';
    const portraitParts = Array.from(
      { length: 6 },
      (_, i) => `${assetBase}part${String(i).padStart(2, '0')}.b64`
    );

    Promise.all(
      portraitParts.map(path =>
        fetch(path, { cache: 'force-cache' }).then(response => {
          if (!response.ok) throw new Error(`Portrait asset failed: ${path}`);
          return response.text();
        })
      )
    )
      .then(chunks => {
        const binary = atob(chunks.map(chunk => chunk.trim()).join(''));
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i += 1) {
          bytes[i] = binary.charCodeAt(i);
        }
        heroPhoto.src = URL.createObjectURL(new Blob([bytes], { type: 'image/webp' }));
        heroPhoto.width = 600;
        heroPhoto.height = 750;
        heroPhoto.style.aspectRatio = '4 / 5';
      })
      .catch(() => {
        heroPhoto.src = 'https://avatars.githubusercontent.com/u/36891933?v=4';
      });
  }

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
    const label = isRu
      ? (isDark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему')
      : (isDark ? 'Switch to light theme' : 'Switch to dark theme');
    themeBtn.setAttribute('aria-label', label);
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
    menuBtn.setAttribute('aria-label', isRu
      ? (open ? 'Закрыть меню' : 'Открыть меню')
      : (open ? 'Close navigation' : 'Open navigation'));
  });

  navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    menuBtn?.setAttribute('aria-expanded', 'false');
    menuBtn?.setAttribute('aria-label', isRu ? 'Открыть меню' : 'Open navigation');
  }));

  const cvRoutes = {
    'Vladimir_Glazatov_Academic_CV.pdf': '/cv/academic/',
    'Vladimir_Glazatov_Theoretical_ML_CV.pdf': '/cv/theoretical-ml/',
    'Vladimir_Glazatov_Mathematics_CV.pdf': '/cv/mathematics/'
  };
  document.querySelectorAll('a[href]').forEach(a => {
    for (const [name, route] of Object.entries(cvRoutes)) {
      if (a.getAttribute('href')?.endsWith(name)) {
        a.setAttribute('href', route);
        if (/download/i.test(a.textContent)) a.textContent = 'Open CV';
        if (/скачать/i.test(a.textContent)) a.textContent = 'Открыть CV';
      }
    }
  });
})();
