#!/usr/bin/env python3
"""
Scrape Steve Madden's open Shopify products.json to fill footwear categories.

Target categories: Boots, Booties, Heels, Sneakers, Flats, Loafers, Sandals.
Writes /tmp/stevemadden.json for the uploader to consume.

USD prices are converted to approximate CAD (× 1.35) — our schema stores a
single `price` integer; we don't track currency per-product.
"""

import json
import time
from pathlib import Path

import requests

BASE = "https://www.stevemadden.com"
USD_TO_CAD = 1.35
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

# Steve Madden `Type:X` tag → our category taxonomy
TYPE_MAP = {
    "Type:Heels": "Heels",
    "Type:Boots": "Boots",
    "Type:Booties": "Boots",
    "Type:Sneakers": "Sneakers",
    "Type:Flats": "Flats",
    "Type:Loafers": "Flats",
    "Type:Sandals": "Flats",  # our taxonomy lumps sandals with flats
}


def infer_category(product: dict) -> str | None:
    for tag in product.get("tags", []):
        if tag in TYPE_MAP:
            return TYPE_MAP[tag]
    return None


def extract_color(product: dict) -> str:
    """Steve Madden variant title is 'COLOR / SIZE / SKU' — take the color."""
    for tag in product.get("tags", []):
        if tag.startswith("Color:"):
            return tag.split(":", 1)[1].strip()
    variants = product.get("variants", [])
    if variants:
        title = variants[0].get("title", "")
        if " / " in title:
            return title.split(" / ")[0].strip()
    return ""


def main():
    products = []
    for page in range(1, 20):
        url = f"{BASE}/products.json?limit=250&page={page}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        batch = data.get("products", [])
        if not batch:
            break
        products.extend(batch)
        print(f"  page {page}: +{len(batch)} (total {len(products)})")
        time.sleep(0.2)

    # Keep only Women's Shoes, with a valid footwear type
    normalized = []
    for p in products:
        if p.get("product_type") != "Women's Shoes":
            continue
        category = infer_category(p)
        if category is None:
            continue
        variants = p.get("variants", [])
        if not variants:
            continue
        usd_price = variants[0].get("price")
        if usd_price is None:
            continue
        try:
            cad = round(float(usd_price) * USD_TO_CAD)
        except (ValueError, TypeError):
            continue
        images = p.get("images", [])
        if not images:
            continue
        image_url = images[0].get("src", "")
        if not image_url:
            continue
        name = p.get("title", "").strip()
        handle = p.get("handle", "")
        color = extract_color(p)
        normalized.append({
            "name": name.title(),  # titles are ALL CAPS — title-case them
            "price": cad,
            "image_url": image_url,
            "product_url": f"{BASE}/products/{handle}",
            "color": color,
            "category_hint": category.lower(),
            "_scraped_category": category,
        })

    out = Path("/tmp/stevemadden.json")
    out.write_text(json.dumps(normalized, indent=2))
    print(f"\n→ Wrote {len(normalized)} products to {out}")

    from collections import Counter
    cats = Counter(p["_scraped_category"] for p in normalized)
    print(f"  Categories: {dict(cats.most_common())}")


if __name__ == "__main__":
    main()
