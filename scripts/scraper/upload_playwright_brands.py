#!/usr/bin/env python3
"""Upload Lululemon, Garage, Dynamite products scraped via Playwright to Supabase."""

import argparse
import glob
import json
import sys

sys.path.insert(0, ".")
from config import SUPABASE_URL, SUPABASE_KEY
from normalize import normalize_product


BRAND_SOURCES = {
    "LULULEMON": {
        "glob": "/tmp/lululemon_*.json",
        "category_hint_from_filename": True,
    },
    "GARAGE": {
        "glob": "/tmp/garage_p*.json",
        "category_hint_from_filename": False,
    },
    "DYNAMITE": {
        "glob": "/tmp/dynamite_p*.json",
        "category_hint_from_filename": False,
    },
}


def load_raw(brand: str) -> list[dict]:
    cfg = BRAND_SOURCES[brand]
    files = sorted(glob.glob(cfg["glob"]))
    items = []
    for path in files:
        with open(path) as f:
            data = json.load(f)
        arr = data if isinstance(data, list) else data.get("items", [])
        if cfg["category_hint_from_filename"]:
            slug = path.rsplit("/", 1)[-1].replace(".json", "").split("_", 1)[1]
            for p in arr:
                p["category_hint"] = slug
        items.extend(arr)
    return items


def normalize_brand(brand: str) -> list[dict]:
    raw = load_raw(brand)
    seen = set()
    out = []
    for r in raw:
        p = normalize_product(r, brand)
        if p is None:
            continue
        if p["image_url"] in seen:
            continue
        seen.add(p["image_url"])
        out.append(p)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--brand", choices=list(BRAND_SOURCES.keys()) + ["ALL"], default="ALL")
    args = parser.parse_args()

    brands = list(BRAND_SOURCES.keys()) if args.brand == "ALL" else [args.brand]

    all_normalized = []
    for brand in brands:
        normalized = normalize_brand(brand)
        print(f"{brand}: {len(normalized)} normalized")
        all_normalized.extend(normalized)

    print(f"Total: {len(all_normalized)}")

    if args.dry_run:
        from collections import Counter
        for brand in brands:
            only = [p for p in all_normalized if p["brand"] == brand]
            cats = Counter(p["category"] for p in only)
            prices = [p["price"] for p in only]
            print(f"\n{brand}:")
            print(f"  Categories: {dict(cats)}")
            if prices:
                print(f"  Prices: ${min(prices)} - ${max(prices)}, avg ${sum(prices)//len(prices)}")
            if only:
                print(f"  Sample: {only[0]}")
        return

    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    existing = set()
    for brand in brands:
        page = 0
        while True:
            resp = (
                client.table("products")
                .select("image_url")
                .eq("brand", brand)
                .range(page * 1000, (page + 1) * 1000 - 1)
                .execute()
            )
            if not resp.data:
                break
            existing.update(row["image_url"] for row in resp.data)
            page += 1
    print(f"Existing in DB for {brands}: {len(existing)}")

    new_products = [p for p in all_normalized if p["image_url"] not in existing]
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
            print(f"  Error on batch {i}: {e}")
            break

    print(f"\nDone: {uploaded} products uploaded")


if __name__ == "__main__":
    main()
