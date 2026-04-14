#!/usr/bin/env python3
"""
Product seed generator — orchestrates scraping, normalization, and DB upload.

Usage:
    # Scrape all brands and upload to Supabase
    python generate_seed.py

    # Scrape specific brands
    python generate_seed.py --brands GARAGE DYNAMITE

    # Dry run (normalize + print, no upload)
    python generate_seed.py --dry-run

    # Export to JSON instead of uploading
    python generate_seed.py --output products.json

Requirements:
    pip install requests beautifulsoup4 supabase
"""

import argparse
import json
import sys

from config import BRANDS, SUPABASE_URL, SUPABASE_KEY
from scrape import scrape_brand
from scrape_shopify import SHOPIFY_BRANDS, scrape_shopify_brand
from normalize import normalize_product

ALL_BRANDS = {**{k: "html" for k in BRANDS}, **{k: "shopify" for k in SHOPIFY_BRANDS}}


def upload_to_supabase(products: list[dict]) -> int:
    """Upload normalized products to Supabase, skipping duplicates by image_url."""
    from supabase import create_client

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch existing image URLs to avoid duplicates
    existing = set()
    page = 0
    while True:
        resp = client.table("products").select("image_url").range(page * 1000, (page + 1) * 1000 - 1).execute()
        if not resp.data:
            break
        existing.update(row["image_url"] for row in resp.data)
        page += 1

    print(f"\nExisting products in DB: {len(existing)}")

    new_products = [p for p in products if p["image_url"] not in existing]
    print(f"New products to upload: {len(new_products)}")

    if not new_products:
        return 0

    # Batch insert (Supabase supports bulk inserts)
    batch_size = 50
    uploaded = 0
    for i in range(0, len(new_products), batch_size):
        batch = new_products[i : i + batch_size]
        try:
            client.table("products").insert(batch).execute()
            uploaded += len(batch)
            print(f"  Uploaded {uploaded}/{len(new_products)}")
        except Exception as e:
            print(f"  ✗ Batch insert error: {e}")

    return uploaded


def main():
    parser = argparse.ArgumentParser(description="Scrape products and seed Supabase DB")
    parser.add_argument(
        "--brands",
        nargs="+",
        choices=list(ALL_BRANDS.keys()),
        default=list(ALL_BRANDS.keys()),
        help="Brands to scrape (default: all)",
    )
    parser.add_argument(
        "--max-per-brand",
        type=int,
        default=60,
        help="Max products per brand (default: 60)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Normalize and print without uploading",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Export to JSON file instead of uploading",
    )
    args = parser.parse_args()

    all_products = []

    for brand in args.brands:
        brand_type = ALL_BRANDS.get(brand, "html")
        if brand_type == "shopify":
            raw = scrape_shopify_brand(brand, max_products=args.max_per_brand)
        else:
            raw = scrape_brand(brand, max_products=args.max_per_brand)

        normalized = []
        for r in raw:
            product = normalize_product(r, brand)
            if product:
                normalized.append(product)

        print(f"\n  {brand}: {len(raw)} scraped → {len(normalized)} normalized")
        all_products.extend(normalized)

    print(f"\n{'='*50}")
    print(f"Total normalized products: {len(all_products)}")

    # Category distribution
    from collections import Counter
    cats = Counter(p["category"] for p in all_products)
    print("\nCategory distribution:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat:12s}: {count}")

    # Brand distribution
    brands = Counter(p["brand"] for p in all_products)
    print("\nBrand distribution:")
    for brand, count in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"  {brand:18s}: {count}")

    if args.dry_run:
        print("\n[DRY RUN] First 3 products:")
        for p in all_products[:3]:
            print(f"  {json.dumps(p, indent=2)}")
        return

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"\nExported to {args.output}")
        return

    uploaded = upload_to_supabase(all_products)
    print(f"\nDone! Uploaded {uploaded} new products to Supabase.")


if __name__ == "__main__":
    main()
