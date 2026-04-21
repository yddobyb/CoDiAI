"""
Direct Algolia API scraper for Aritzia.

Aritzia uses Algolia for product search. The public search key is discoverable
from browser devtools (Network tab on aritzia.com, filter by 'algolia'). This
scraper bypasses browser rendering entirely.

Set these before running (keys rotate per browser session but are typically
stable for 30+ days):
    export ARITZIA_ALGOLIA_APP_ID="<found in request URL>"
    export ARITZIA_ALGOLIA_API_KEY="<found in x-algolia-api-key header>"

Usage:
    python aritzia_algolia.py shoes --category-filter shoes
    python aritzia_algolia.py coats --category-filter coats-and-jackets
    python aritzia_algolia.py boots --category-filter shoes --refinement-color Black
"""

import argparse
import json
import os
import urllib.parse
from pathlib import Path
import requests

APP_ID = os.environ.get("ARITZIA_ALGOLIA_APP_ID", "")
API_KEY = os.environ.get("ARITZIA_ALGOLIA_API_KEY", "")
if not APP_ID or not API_KEY:
    raise RuntimeError(
        "Missing ARITZIA_ALGOLIA_APP_ID / ARITZIA_ALGOLIA_API_KEY env vars. "
        "Extract from aritzia.com devtools Network tab (search-0.aritzia.com request)."
    )
INDEX = "production_ecommerce_aritzia__Aritzia_CA__products__en_CA"
ENDPOINT = f"https://search-0.aritzia.com/1/indexes/*/queries"

HEADERS = {
    "x-algolia-api-key": API_KEY,
    "x-algolia-application-id": APP_ID,
    "content-type": "application/x-www-form-urlencoded",
    "referer": "https://www.aritzia.com/",
    "user-agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "accept-language": "en-CA",
}


def fetch_all(category_filter: str, hits_per_page: int = 100) -> list[dict]:
    """Query Algolia for every hit in a category."""
    all_hits: list[dict] = []
    page = 0
    while True:
        params = urllib.parse.urlencode({
            "hitsPerPage": hits_per_page,
            "page": page,
            "filters": f"categories:{category_filter} AND (orderable:true OR searchableIfUnavailable:true)",
        })
        payload = {"requests": [{"indexName": INDEX, "query": "", "params": params}]}
        r = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        result = data["results"][0]
        hits = result.get("hits", [])
        all_hits.extend(hits)
        n_pages = result.get("nbPages", 1)
        print(f"  page {page + 1}/{n_pages} → {len(hits)} hits (total: {len(all_hits)}/{result.get('nbHits')})")
        page += 1
        if page >= n_pages:
            break
    return all_hits


def normalize(hit: dict) -> dict | None:
    """Convert Algolia hit to our standard product dict."""
    price_obj = hit.get("price") or {}
    price = price_obj.get("min") if isinstance(price_obj, dict) else price_obj
    if price is None:
        return None
    slug = hit.get("slug", "")
    if not slug:
        return None
    default_image = hit.get("defaultImage", "")
    if not default_image:
        return None
    image_url = f"https://assets.aritzia.com/image/upload/f_auto,q_auto,w_900/{default_image}"
    product_url = f"https://www.aritzia.com/us/en/product/{slug}"
    # Prefer trueColor (human name) over color ID
    color = hit.get("trueColor") or hit.get("refinementColor") or ""
    if isinstance(color, list):
        color = color[0] if color else ""
    color = str(color).lower()
    # Prefer c_displayName (has full product title)
    name = hit.get("c_displayName") or hit.get("name") or ""
    # Category hint from hierarchicalCategories
    hc = hit.get("hierarchicalCategories") or {}
    category_hint = ""
    if isinstance(hc, dict):
        for lvl in ("2", "1", "lvl2", "lvl1"):
            if lvl in hc:
                category_hint = hc[lvl].split(">")[-1].strip()
                break
    return {
        "name": name,
        "price": float(price),
        "image_url": image_url,
        "product_url": product_url,
        "color": color,
        "category_hint": category_hint,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_name", help="output basename, e.g. 'shoes' → /tmp/aritzia_shoes.json")
    ap.add_argument("--category-filter", required=True, help="Algolia categories filter, e.g. 'shoes', 'coats-and-jackets'")
    ap.add_argument("--hits-per-page", type=int, default=100)
    args = ap.parse_args()

    print(f"→ Fetching Aritzia category='{args.category_filter}'")
    hits = fetch_all(args.category_filter, args.hits_per_page)

    normalized = [n for n in (normalize(h) for h in hits) if n]
    # Dedupe by product_url
    seen = set()
    unique = []
    for p in normalized:
        if p["product_url"] not in seen:
            seen.add(p["product_url"])
            unique.append(p)

    out_path = Path("/tmp") / f"aritzia_{args.output_name}.json"
    out_path.write_text(json.dumps(unique, indent=2, ensure_ascii=False))
    print(f"\n✓ {len(unique)} unique products → {out_path}")
    if unique:
        print(f"  sample: {unique[0]}")


if __name__ == "__main__":
    main()
