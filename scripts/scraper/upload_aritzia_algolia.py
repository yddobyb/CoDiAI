#!/usr/bin/env python3
"""
Upload new Aritzia products scraped via Algolia API to Supabase.

Reads /tmp/aritzia_<cat>.json files produced by aritzia_algolia.py, normalizes
them against the products table schema, deduplicates against existing rows
(keyed by affiliate_url — product_url — since Aritzia image_urls include a
season code that changes across scrapes), and inserts new rows.

Also runs a one-off brand-name cleanup: UPDATE brand 'Oak+Fort' → 'OAK + FORT'.

Usage:
    export SUPABASE_URL="https://<project>.supabase.co"
    export SUPABASE_KEY="<service_role key or publishable>"
    python upload_aritzia_algolia.py              # upload
    python upload_aritzia_algolia.py --dry-run    # preview counts
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import SUPABASE_URL, SUPABASE_KEY
from normalize import normalize_product


# Filename → category_hint (keyword passed to normalize_product so category
# inference works on products whose name doesn't obviously contain the word).
CATEGORY_FILES = {
    "shoes": "sneaker",   # Aritzia footwear is mostly sneakers/loafers — default to sneaker for unmatched names
    "coats": "coat",
    "jackets": "jacket",
    "sweaters": "sweater",
    "jeans": "jeans",
    "sweatshirts": "hoodie",
    "puffers": "jacket",  # puffer → Jacket per CATEGORY_MAP
}


def load_all() -> list[dict]:
    raw_items = []
    for cat_slug, hint in CATEGORY_FILES.items():
        path = Path(f"/tmp/aritzia_{cat_slug}.json")
        if not path.exists():
            print(f"  (skipping — missing {path})")
            continue
        arr = json.loads(path.read_text())
        for p in arr:
            # Map our scraper's product_url → affiliate_url
            p.setdefault("affiliate_url", p.get("product_url"))
            # Force-override category_hint: Algolia populates it with brand names
            # (e.g. "G.H.BASS"), which would defeat our keyword-based category inference.
            if hint:
                p["category_hint"] = hint
            raw_items.append(p)
        print(f"  loaded {len(arr)} from {path.name} (hint='{hint}')")
    return raw_items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("→ Loading scraped JSON files")
    raw = load_all()
    print(f"Total raw: {len(raw)}")

    normalized = []
    seen_urls = set()
    dropped_no_cat = 0
    dropped_bad_price = 0
    for r in raw:
        before = (r.get("name"), r.get("price"))
        p = normalize_product(r, "ARITZIA")
        if p is None:
            if not r.get("name"):
                dropped_no_cat += 1
            else:
                name_l = r["name"].lower()
                hint_l = (r.get("category_hint") or "").lower()
                if any(w in name_l for w in ("sneaker", "loafer", "boot", "sandal", "heel", "flat")) or hint_l:
                    dropped_bad_price += 1
                else:
                    dropped_no_cat += 1
            continue
        key = p.get("affiliate_url") or p["image_url"]
        if key in seen_urls:
            continue
        seen_urls.add(key)
        normalized.append(p)

    print(f"Normalized: {len(normalized)} (dropped no-category: {dropped_no_cat}, bad-price: {dropped_bad_price})")

    if args.dry_run:
        from collections import Counter
        cats = Counter(p["category"] for p in normalized)
        print(f"Categories: {dict(sorted(cats.items(), key=lambda x: -x[1]))}")
        colors = Counter(p["color"] for p in normalized)
        print(f"Colors: {dict(colors)}")
        prices = [p["price"] for p in normalized]
        print(f"Price range: ${min(prices)} - ${max(prices)}, avg ${sum(prices)//len(prices)}")
        print(f"Sample: {normalized[0]}")
        return

    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # ── 1. One-off brand-name cleanup: Oak+Fort → OAK + FORT ──
    print("\n→ Merging 'Oak+Fort' → 'OAK + FORT'")
    resp = client.table("products").update({"brand": "OAK + FORT"}).eq("brand", "Oak+Fort").execute()
    print(f"  updated {len(resp.data or [])} rows")

    # ── 2. Dedupe against existing Aritzia rows ──
    print("\n→ Fetching existing Aritzia rows")
    existing_urls = set()
    page = 0
    while True:
        resp = (
            client.table("products")
            .select("image_url, affiliate_url")
            .eq("brand", "ARITZIA")
            .range(page * 1000, (page + 1) * 1000 - 1)
            .execute()
        )
        if not resp.data:
            break
        for row in resp.data:
            existing_urls.add(row.get("affiliate_url") or row.get("image_url"))
        page += 1
    print(f"  existing Aritzia: {len(existing_urls)}")

    new_products = [p for p in normalized if (p.get("affiliate_url") or p["image_url"]) not in existing_urls]
    print(f"  new to upload: {len(new_products)}")

    if not new_products:
        print("Nothing to do.")
        return

    # ── 3. Batch insert ──
    batch_size = 50
    uploaded = 0
    for i in range(0, len(new_products), batch_size):
        batch = new_products[i:i + batch_size]
        try:
            client.table("products").insert(batch).execute()
            uploaded += len(batch)
            print(f"  {uploaded}/{len(new_products)}")
        except Exception as e:
            print(f"  Error on batch {i // batch_size}: {e}")
            break

    print(f"\n✓ Uploaded {uploaded} new Aritzia products")


if __name__ == "__main__":
    main()
