#!/usr/bin/env python3
"""
Upload Steve Madden women's shoes scraped via stevemadden_shopify.py to Supabase.

Reads /tmp/stevemadden.json, normalizes, dedupes against existing STEVE MADDEN
rows (keyed by affiliate_url), and batch-inserts.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import SUPABASE_URL, SUPABASE_KEY
from normalize import normalize_color, normalize_style, parse_price


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path("/tmp/stevemadden.json")
    if not src.exists():
        print(f"Missing {src} — run stevemadden_shopify.py first")
        sys.exit(1)

    raw = json.loads(src.read_text())
    print(f"Raw products loaded: {len(raw)}")

    # Trust the scraper's Shopify-tag-based category instead of name-substring inference.
    # Many shoe names contain words like "boot" or "sneaker" that cause the generic
    # normalize_category to mis-bucket (e.g., "Sally Scarf Chestnut Suede" is a boot but
    # matches "sweater"/"jeans" on unrelated substrings).
    normalized = []
    seen_urls = set()
    dropped = 0
    for r in raw:
        affiliate_url = r.get("product_url")
        image_url = r.get("image_url", "").strip()
        name = r.get("name", "").strip()
        category = r.get("_scraped_category")
        price = parse_price(r.get("price"))
        if not (name and image_url and category and price and 5 <= price <= 500):
            dropped += 1
            continue
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        key = affiliate_url or image_url
        if key in seen_urls:
            continue
        seen_urls.add(key)
        normalized.append({
            "name": name,
            "brand": "STEVE MADDEN",
            "category": category,
            "color": normalize_color(r.get("color", ""), name),
            "style": normalize_style(name, category),
            "price": price,
            "image_url": image_url,
            "affiliate_url": affiliate_url,
        })

    print(f"Normalized: {len(normalized)} (dropped: {dropped})")

    if args.dry_run:
        from collections import Counter
        cats = Counter(p["category"] for p in normalized)
        print(f"Categories: {dict(cats.most_common())}")
        colors = Counter(p["color"] for p in normalized)
        print(f"Colors: {dict(colors.most_common())}")
        print(f"Sample: {normalized[0]}")
        return

    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Dedupe against existing Steve Madden rows
    print("\n→ Fetching existing STEVE MADDEN rows")
    existing_urls = set()
    page = 0
    while True:
        resp = (
            client.table("products")
            .select("image_url, affiliate_url")
            .eq("brand", "STEVE MADDEN")
            .range(page * 1000, (page + 1) * 1000 - 1)
            .execute()
        )
        if not resp.data:
            break
        for row in resp.data:
            existing_urls.add(row.get("affiliate_url") or row.get("image_url"))
        page += 1
    print(f"  existing: {len(existing_urls)}")

    new_products = [p for p in normalized if (p.get("affiliate_url") or p["image_url"]) not in existing_urls]
    print(f"  new to upload: {len(new_products)}")

    if not new_products:
        print("Nothing to do.")
        return

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

    print(f"\n✓ Uploaded {uploaded} new Steve Madden products")


if __name__ == "__main__":
    main()
