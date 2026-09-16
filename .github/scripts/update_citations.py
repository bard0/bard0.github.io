#!/usr/bin/env python3

import difflib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "data" / "citations.json"
EMAIL = "glazv96@yandex.ru"
API = "https://api.openalex.org"
API_KEY = os.environ.get("OPENALEX_API_KEY", "").strip()

WORKS = {
    "10.1134/S1995080225605624": {
        "title": "Analysis of Exploding Solutions of an Infinite-Dimensional Linear Hamiltonian System in Phase Space Extensions",
        "year": 2025,
    },
    "10.1134/S1995080225608070": {
        "title": "Continuation of Solutions of Differential Equations through the Formation of Singularities",
        "year": 2025,
    },
    "10.52452/00213462_2025_68_05_496": {
        "title": "Dynamics of Nonlinear Wave Systems Admitting Singularity Formation",
        "year": 2025,
        "alt_titles": ["Динамика нелинейных волновых систем, допускающая формирование особенностей"],
    },
    "10.1134/S1995080224603138": {
        "title": "Measure of the Banach Limit on L∞(R)",
        "year": 2024,
    },
    "10.13108/2022-14-2-3": {
        "title": "Measures on Hilbert Space Invariant with Respect to Hamiltonian Flows",
        "year": 2022,
    },
    "10.20948/prepr-2022-99": {
        "title": "On the Koopman Representation of Hamiltonian Flows in Infinite Dimensional Spaces with Invariant Measure",
        "year": 2022,
        "alt_titles": ["О купмановском представлении гамильтоновых потоков в бесконечномерных пространствах с инвариантной мерой"],
    },
}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w]+", " ", (text or "").lower())).strip()


def request_json(path: str, params: dict) -> dict:
    query = dict(params)
    query["mailto"] = EMAIL
    if API_KEY:
        query["api_key"] = API_KEY
    url = f"{API}{path}?{urllib.parse.urlencode(query)}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"bard0.github.io citation updater ({EMAIL})",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def load_previous() -> dict:
    if not OUT.exists():
        return {"source": "OpenAlex", "updated_at": None, "works": {}}
    try:
        with OUT.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"source": "OpenAlex", "updated_at": None, "works": {}}


def key_for_doi(doi: str) -> str:
    return f"doi:{doi.lower()}"


def work_entry(work: dict) -> dict:
    openalex_id = work.get("id")
    return {
        "count": work.get("cited_by_count"),
        "openalex_id": openalex_id,
        "openalex_url": openalex_id,
        "title": work.get("display_name"),
    }


def fallback_entry(previous: dict, doi: str, title: str) -> dict:
    return previous.get("works", {}).get(key_for_doi(doi), {
        "count": None,
        "openalex_id": None,
        "openalex_url": None,
        "title": title,
    })


def author_text(item: dict) -> str:
    return " ".join(
        (a.get("author") or {}).get("display_name", "")
        for a in item.get("authorships", [])
    ).lower()


def search_fallback(meta: dict) -> dict | None:
    titles = [meta["title"], *meta.get("alt_titles", [])]
    best = None
    best_score = 0.0

    for query_title in titles:
        data = request_json(
            "/works",
            {
                "search": query_title,
                "filter": f"publication_year:{meta['year']}",
                "per_page": 10,
                "select": "id,display_name,cited_by_count,publication_year,authorships,doi",
            },
        )
        for item in data.get("results", []):
            candidate = norm(item.get("display_name", ""))
            score = max(
                difflib.SequenceMatcher(None, norm(title), candidate).ratio()
                for title in titles
            )
            authors = author_text(item)
            if "glazatov" in authors or "глазатов" in authors:
                score += 0.15
            if score > best_score:
                best_score = score
                best = item

    return best if best is not None and best_score >= 0.72 else None


def fetch_works(previous: dict) -> tuple[dict, bool]:
    resolved = {}
    request_ok = True

    try:
        data = request_json(
            "/works",
            {
                "filter": "doi:" + "|".join(WORKS),
                "per_page": 100,
                "select": "id,display_name,cited_by_count,doi",
            },
        )
        for item in data.get("results", []):
            doi = (item.get("doi") or "").lower().replace("https://doi.org/", "")
            if doi:
                resolved[doi] = item
    except Exception as exc:
        request_ok = False
        print(f"OpenAlex DOI lookup failed: {exc}", file=sys.stderr)

    works = {}
    for doi, meta in WORKS.items():
        key = key_for_doi(doi)
        item = resolved.get(doi.lower())

        if item is None:
            try:
                item = search_fallback(meta)
                if item is not None:
                    print(f"Resolved {doi} by title fallback: {item.get('display_name')}")
            except Exception as exc:
                request_ok = False
                print(f"OpenAlex title fallback failed for {doi}: {exc}", file=sys.stderr)

        works[key] = work_entry(item) if item is not None else fallback_entry(previous, doi, meta["title"])

    return works, request_ok


def main() -> int:
    previous = load_previous()
    works, request_ok = fetch_works(previous)

    if not request_ok and not any(isinstance(v.get("count"), int) for v in works.values()):
        print("No citation data could be retrieved and no usable cache exists.", file=sys.stderr)
        return 1

    if works == previous.get("works", {}):
        print("Citation counts unchanged.")
        return 0

    payload = {
        "source": "OpenAlex",
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "works": works,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    count = sum(isinstance(v.get("count"), int) for v in works.values())
    print(f"Updated citation data for {count}/{len(WORKS)} works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
