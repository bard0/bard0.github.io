(() => {
  const root = document.documentElement;
  const themeBtn = document.querySelector('[data-theme-toggle]');
  const menuBtn = document.querySelector('[data-menu-toggle]');
  const navLinks = document.querySelector('.nav-links');
  const isRu = (root.lang || '').toLowerCase().startsWith('ru');
  const heroPhoto = document.querySelector('.hero-photo');

  if (heroPhoto) {
    const assetBase = isRu ? '../assets/img/profile-v8/' : 'assets/img/profile-v8/';
    const portraitParts = ['part0.b64','part1.b64','part2.b64','part3a.b64','part3b.b64','part4a.b64','part4b.b64'].map(name => `${assetBase}${name}`);
    Promise.all(portraitParts.map(path => fetch(path, { cache: 'force-cache' }).then(response => {
      if (!response.ok) throw new Error(`Portrait asset failed: ${path}`);
      return response.text();
    }))).then(chunks => {
      const binary = atob(chunks.map(chunk => chunk.trim()).join(''));
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
      heroPhoto.src = URL.createObjectURL(new Blob([bytes], { type: 'image/jpeg' }));
      heroPhoto.width = 320;
      heroPhoto.height = 320;
      heroPhoto.style.aspectRatio = '1 / 1';
    }).catch(() => { heroPhoto.src = 'https://avatars.githubusercontent.com/u/36891933?v=4'; });
  }

  document.querySelectorAll('.hero-meta span').forEach(item => {
    const text = item.textContent.trim().toLowerCase();
    if (text.includes('math-net citations') || text.includes('цитирования math-net')) item.remove();
  });

  const skills = document.querySelector('#background .chips');
  if (skills && ![...skills.querySelectorAll('.chip')].some(chip => /llm/i.test(chip.textContent))) {
    const agentSkill = document.createElement('span');
    agentSkill.className = 'chip';
    agentSkill.textContent = isRu ? 'LLM-агенты / агентные рабочие процессы' : 'LLM agents / agentic workflows';
    skills.appendChild(agentSkill);
  }

  const publicationKey = publication => {
    const doiLink = publication.querySelector('a[href*="doi.org/"]');
    if (doiLink) {
      try {
        const doi = new URL(doiLink.href).pathname.replace(/^\//, '').toLowerCase();
        return `doi:${doi}`;
      } catch (_) { return null; }
    }
    const title = publication.querySelector('.pub-title')?.textContent.trim().toLowerCase() || '';
    return title.includes('купмановском представлении гамильтоновых потоков')
      ? 'doi:10.20948/prepr-2022-99'
      : null;
  };

  const citationTargets = [];
  document.querySelectorAll('.pub').forEach(publication => {
    const key = publicationKey(publication);
    const links = publication.querySelector('.pub-links');
    if (!key || !links) return;
    const badge = document.createElement('a');
    badge.className = 'citation-count';
    badge.hidden = true;
    badge.target = '_blank';
    badge.rel = 'noopener noreferrer';
    badge.dataset.citationKey = key;
    links.appendChild(badge);
    citationTargets.push(badge);
  });

  if (citationTargets.length) {
    const citationDataPath = isRu ? '../assets/data/citations.json' : 'assets/data/citations.json';
    fetch(citationDataPath, { cache: 'no-cache' })
      .then(response => { if (!response.ok) throw new Error('Citation data unavailable'); return response.json(); })
      .then(data => citationTargets.forEach(badge => {
        const entry = data?.works?.[badge.dataset.citationKey];
        if (!entry || !Number.isInteger(entry.count)) return;
        badge.textContent = isRu ? `${entry.count} цит. · OpenAlex` : `${entry.count} ${entry.count === 1 ? 'citation' : 'citations'} · OpenAlex`;
        badge.href = entry.openalex_url || 'https://openalex.org/';
        badge.title = data.updated_at ? `${isRu ? 'Данные OpenAlex, обновлено' : 'OpenAlex data, updated'} ${data.updated_at.slice(0, 10)}` : 'OpenAlex';
        badge.hidden = false;
      }))
      .catch(() => {});
  }

  const stored = localStorage.getItem('vg-theme');
  if (stored === 'light' || stored === 'dark') root.dataset.theme = stored;
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) root.dataset.theme = 'dark';

  const updateThemeLabel = () => {
    if (!themeBtn) return;
    const isDark = root.dataset.theme === 'dark';
    themeBtn.textContent = isDark ? '☀' : '☾';
    const label = isRu ? (isDark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему') : (isDark ? 'Switch to light theme' : 'Switch to dark theme');
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
    menuBtn.setAttribute('aria-label', isRu ? (open ? 'Закрыть меню' : 'Открыть меню') : (open ? 'Close navigation' : 'Open navigation'));
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
