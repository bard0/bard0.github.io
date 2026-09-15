# Vladimir Glazatov - GitHub Pages research site

Static, dependency-free personal research website prepared for `bard0.github.io`.

## What is included

- English homepage (`index.html`)
- Russian mirror (`ru/index.html`)
- Responsive light/dark design
- Research, publications, talks, background, CV and contact sections
- Three downloadable CV PDFs
- Portrait loaded from the GitHub profile avatar
- SEO metadata + Person JSON-LD
- `robots.txt`, `sitemap.xml`, favicon and 404 page
- No analytics or tracking

## Deploy on GitHub Pages

1. Create a public GitHub repository named **`bard0.github.io`**.
2. Copy the contents of this folder into the repository root.
3. Commit and push to the `main` branch.
4. In GitHub: **Settings -> Pages**.
5. Under **Build and deployment**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`.
6. The site should appear at `https://bard0.github.io/` after the Pages deployment completes.

No build step is required.

## Local preview

From this directory:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/`.

## Updating the research project

The main public research summary is in the `#research` section of both language pages. Keep the website at the level of externally meaningful results; internal experiment labels such as M9/G8 should stay in the research repository, not on the homepage.

Recommended update policy:

- promote only theorem-level, controlled numerical, or clearly labeled exploratory results;
- keep exact experimental bookkeeping in GitHub/Drive;
- update the two homepage metrics only after a new frozen comparison supersedes the current controlled result;
- once the SGD manuscript becomes public, replace or supplement the GitHub link with the paper/preprint link.

## CV files

Files under `downloads/` are the September 2026 versions:

- `Vladimir_Glazatov_Academic_CV.pdf`
- `Vladimir_Glazatov_Theoretical_ML_CV.pdf`
- `Vladimir_Glazatov_Mathematics_CV.pdf`

Replace them in place when CVs are updated so external links remain stable.

## Custom domain (optional)

1. Buy/configure a domain, for example `vladimirglazatov.com`.
2. Rename `CNAME.example` to `CNAME` and put the domain name inside.
3. Configure the required GitHub Pages DNS records at the registrar.
4. Enable **Enforce HTTPS** in GitHub Pages settings after DNS propagation.

## Design principle

This is intentionally a research website rather than a software-developer portfolio: the hierarchy is research question -> contribution -> evidence -> publication record -> background.
