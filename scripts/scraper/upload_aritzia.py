#!/usr/bin/env python3
"""Upload 547 Aritzia products scraped via Playwright to Supabase."""

import argparse
import json
import sys

sys.path.insert(0, ".")
from config import SUPABASE_URL, SUPABASE_KEY
from normalize import normalize_product


CATEGORY_HINT = {
    "dresses": "dress",
    "tops": "shirt",
    "pants": "pants",
    "skirts": "skirt",
}


def load_aritzia_products() -> list[dict]:
    items = []
    for cat_slug, hint in CATEGORY_HINT.items():
        path = f"/tmp/aritzia_{cat_slug}.json"
        with open(path) as f:
            arr = json.load(f)
        for p in arr:
            p["category_hint"] = hint
            items.append(p)
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    raw = load_aritzia_products()
    print(f"Loaded {len(raw)} raw Aritzia products")

    normalized = []
    seen = set()
    for r in raw:
        product = normalize_product(r, "ARITZIA")
        if product is None:
            continue
        if product["image_url"] in seen:
            continue
        seen.add(product["image_url"])
        normalized.append(product)

    print(f"Normalized: {len(normalized)}")

    if args.dry_run:
        from collections import Counter
        cats = Counter(p["category"] for p in normalized)
        print(f"Categories: {dict(cats)}")
        colors = Counter(p["color"] for p in normalized)
        print(f"Colors: {dict(colors)}")
        prices = [p["price"] for p in normalized]
        print(f"Price range: ${min(prices)} - ${max(prices)}, avg ${sum(prices)//len(prices)}")
        print(f"Sample: {normalized[0]}")
        return

    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    existing = set()
    page = 0
    while True:
        resp = client.table("products").select("image_url").eq("brand", "ARITZIA").range(page * 1000, (page + 1) * 1000 - 1).execute()
        if not resp.data:
            break
        existing.update(row["image_url"] for row in resp.data)
        page += 1

    print(f"Existing Aritzia in DB: {len(existing)}")
    new_products = [p for p in normalized if p["image_url"] not in existing]
    print(f"New to upload: {len(new_products)}")

    if not new_products:
        return

    batch_size = 50
    uploaded = 0
    for i in range(0, len(new_products), batch_size):
        batch = new_products[i:i + batch_size]
        try:
            client.table("products").insert(batch).execute()
            uploaded += len(batch)
            print(f"  Uploaded {uploaded}/{len(new_products)}")
        except Exception as e:
            print(f"  Error: {e}")
            break

    print(f"\nDone: {uploaded} products uploaded")


if __name__ == "__main__":
    main()
