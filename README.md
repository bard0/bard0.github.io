# Vladimir Glazatov — research website

Static personal research website published at `https://bard0.github.io/`.

## Structure

- English homepage: `index.html`
- Russian homepage: `ru/index.html`
- Web CVs:
  - `cv/academic/`
  - `cv/theoretical-ml/`
  - `cv/mathematics/`
- Shared styles and scripts under `assets/`
- `robots.txt`, `sitemap.xml`, favicon and `404.html`
- No analytics or tracking

The site is intentionally dependency-free and requires no build step.

## Content policy

The homepage presents externally meaningful research results rather than the internal experiment log. Internal experiment identifiers, failed hypotheses and exploratory bookkeeping remain in the research repository and project archive.

For the SGD section, keep theorem-level results clearly separated from controlled numerical evidence. Update the displayed matched-system metrics only when a new frozen evaluation supersedes the current controlled comparison.

## Local preview

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/`.

## Deployment

GitHub Pages deploys the `main` branch. Changes should be developed on a separate branch and reviewed before merging into `main`.

## Custom domain

If a custom domain is added later, create a `CNAME` file only when the DNS records are ready and then enable HTTPS in GitHub Pages settings.
