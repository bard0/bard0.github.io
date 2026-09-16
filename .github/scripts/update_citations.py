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

DOI_WORKS = [
    "10.1134/S1995080225605624",
    "10.1134/S1995080225608070",
    "10.52452/00213462_2025_68_05_496",
    "10.1134/S1995080224603138",
    "10.13108/2022-14-2-3",
]

PREPRINT_KEY = "keldysh-2022-99"
PREPRINT_TITLE = "О купмановском представлении гамильтоновых потоков в бесконечномерных пространствах с инвариантной мерой"


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


def work_entry(work: dict) -> dict:
    openalex_id = work.get("id")
    return {
        "count": work.get("cited_by_count"),
        "openalex_id": openalex_id,
        "openalex_url": openalex_id,
        "title": work.get("display_name"),
    }


def fetch_doi_works(previous: dict) -> tuple[dict, bool]:
    works = {}
    ok = True
    try:
        data = request_json(
            "/works",
            {
                "filter": "doi:" + "|".join(DOI_WORKS),
                "per_page": 100,
                "select": "id,display_name,cited_by_count,doi",
            },
        )
        by_doi = {}
        for item in data.get("results", []):
            doi = (item.get("doi") or "").lower().replace("https://doi.org/", "")
            if doi:
                by_doi[doi] = item

        for doi in DOI_WORKS:
            key = f"doi:{doi.lower()}"
            item = by_doi.get(doi.lower())
            if item:
                works[key] = work_entry(item)
            else:
                works[key] = previous.get("works", {}).get(key, {
                    "count": None,
                    "openalex_id": None,
                    "openalex_url": None,
                    "title": None,
                })
    except Exception as exc:
        ok = False
        print(f"OpenAlex DOI lookup failed: {exc}", file=sys.stderr)
        for doi in DOI_WORKS:
            key = f"doi:{doi.lower()}"
            works[key] = previous.get("works", {}).get(key, {
                "count": None,
                "openalex_id": None,
                "openalex_url": None,
                "title": None,
            })
    return works, ok


def fetch_preprint(previous: dict) -> tuple[dict, bool]:
    fallback = previous.get("works", {}).get(PREPRINT_KEY, {
        "count": None,
        "openalex_id": None,
        "openalex_url": None,
        "title": PREPRINT_TITLE,
    })
    try:
        data = request_json(
            "/works",
            {
                "search": PREPRINT_TITLE,
                "filter": "publication_year:2022",
                "per_page": 10,
                "select": "id,display_name,cited_by_count,publication_year,authorships",
            },
        )
        target = norm(PREPRINT_TITLE)
        best = None
        best_score = 0.0
        for item in data.get("results", []):
            candidate = norm(item.get("display_name", ""))
            score = difflib.SequenceMatcher(None, target, candidate).ratio()
            authors = " ".join(
                (a.get("author") or {}).get("display_name", "")
                for a in item.get("authorships", [])
            ).lower()
            if "glazatov" in authors or "глазатов" in authors:
                score += 0.15
            if score > best_score:
                best_score = score
                best = item

        if best is not None and best_score >= 0.72:
            return work_entry(best), True
        print("OpenAlex preprint lookup returned no confident match; keeping previous value.")
        return fallback, True
    except Exception as exc:
        print(f"OpenAlex preprint lookup failed: {exc}", file=sys.stderr)
        return fallback, False


def main() -> int:
    previous = load_previous()
    doi_entries, doi_ok = fetch_doi_works(previous)
    preprint_entry, preprint_ok = fetch_preprint(previous)

    works = dict(doi_entries)
    works[PREPRINT_KEY] = preprint_entry

    if not doi_ok and not preprint_ok and not previous.get("works"):
        print("No citation data could be retrieved and no cache exists.", file=sys.stderr)
        return 1

    comparable_previous = previous.get("works", {})
    if works == comparable_previous:
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

    print(f"Updated citation data for {sum(isinstance(v.get('count'), int) for v in works.values())} works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
