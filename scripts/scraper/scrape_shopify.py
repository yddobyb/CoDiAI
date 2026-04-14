"""
Shopify JSON API scraper for stores that expose /products.json.

Works for: Oak+Fort, Frank&Oak, Kotn, and other Shopify-based stores.
These stores block HTML scraping but expose a JSON product catalog API.

Usage:
    from scrape_shopify import scrape_shopify_brand
    products = scrape_shopify_brand("OAK + FORT", max_products=100)
"""

import time
import requests
from config import REQUEST_DELAY

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept": "application/json",
}

# ── Shopify brand configs ──
SHOPIFY_BRANDS = {
    "OAK + FORT": {
        "base_url": "https://www.oakandfort.com",
        "collection": "all-womens",
        "brand_name": "OAK + FORT",
        "excluded_types": {"Earring", "Bags", "Glasses", "Hats", "Scarves",
                           "Necklace", "Hosiery", "Belt", "Ring", "Bracelet"},
    },
    "FRANK AND OAK": {
        "base_url": "https://ca.frankandoak.com",
        "collection": None,  # No women's collection; filter by tags
        "brand_name": "FRANK AND OAK",
        "gender_filter": "womens",  # Tag must contain this
        "excluded_types": {"Accessories", "Bags", "Hat", "Socks"},
    },
}


def _fetch_collection_products(base_url: str, collection: str | None, limit: int = 250) -> list[dict]:
    """Fetch all products from a Shopify store, paginating through results."""
    all_products = []
    page = 1

    while len(all_products) < limit:
        if collection:
            url = f"{base_url}/collections/{collection}/products.json?limit=250&page={page}"
        else:
            url = f"{base_url}/products.json?limit=250&page={page}"

        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            products = resp.json().get("products", [])
        except Exception as e:
            print(f"  Error fetching page {page}: {e}")
            break

        if not products:
            break

        all_products.extend(products)
        print(f"  Page {page}: {len(products)} products (total: {len(all_products)})")
        page += 1
        time.sleep(REQUEST_DELAY)

    return all_products[:limit]


def _extract_color(product: dict) -> str:
    """Extract primary color from Shopify product options."""
    for option in product.get("options", []):
        if option["name"].lower() == "color":
            values = option.get("values", [])
            if values:
                return values[0]  # First color variant
    return ""


def _extract_image(product: dict) -> str:
    """Get the primary product image URL."""
    images = product.get("images", [])
    if images:
        return images[0].get("src", "")
    return ""


def _extract_price(product: dict) -> str:
    """Get the first variant's price."""
    variants = product.get("variants", [])
    if variants:
        return variants[0].get("price", "")
    return ""


def _matches_gender(product: dict, gender_filter: str | None) -> bool:
    """Check if product tags indicate the target gender."""
    if gender_filter is None:
        return True
    tags = product.get("tags", [])
    return any(gender_filter in str(t).lower() for t in tags)


def scrape_shopify_brand(brand_key: str, max_products: int = 200) -> list[dict]:
    """
    Scrape products from a Shopify store's JSON API.

    Returns list of raw product dicts ready for normalize_product().
    """
    cfg = SHOPIFY_BRANDS.get(brand_key)
    if cfg is None:
        print(f"Unknown Shopify brand: {brand_key}")
        return []

    print(f"\n{'='*50}")
    print(f"Scraping {brand_key} via Shopify API")
    print(f"{'='*50}")

    raw_products = _fetch_collection_products(
        cfg["base_url"], cfg.get("collection"), limit=max_products * 2
    )

    print(f"  Raw products fetched: {len(raw_products)}")

    # Filter and transform
    excluded = cfg.get("excluded_types", set())
    gender = cfg.get("gender_filter")
    results = []

    for p in raw_products:
        if len(results) >= max_products:
            break

        product_type = p.get("product_type", "")

        # Skip excluded types (accessories, jewelry, etc.)
        if product_type in excluded:
            continue

        # Gender filter
        if not _matches_gender(p, gender):
            continue

        image_url = _extract_image(p)
        if not image_url:
            continue

        results.append({
            "name": p.get("title", "").strip(),
            "price": _extract_price(p),
            "color": _extract_color(p),
            "image_url": image_url,
            "category_hint": product_type,
            "affiliate_url": f"{cfg['base_url']}/products/{p.get('handle', '')}",
        })

    print(f"  Filtered products: {len(results)}")
    return results
