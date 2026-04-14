"""
Normalize raw scraped product data to match the products table schema.

Handles:
- Category inference from product name/breadcrumb
- Color normalization to 12-color palette
- Style inference
- Price parsing (CAD)
- Brand name uppercasing
"""

import re
from config import CATEGORY_MAP, COLOR_MAP, STYLE_MAP, DEFAULT_STYLE


def normalize_category(raw_name: str, raw_breadcrumb: str = "") -> str | None:
    """Infer one of our 15 categories from product name and breadcrumb."""
    text = f"{raw_name} {raw_breadcrumb}".lower()

    # Try longest match first to avoid "t-shirt" matching "shirt"
    sorted_keys = sorted(CATEGORY_MAP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in text:
            return CATEGORY_MAP[key]

    return None  # Unknown category — skip this product


def normalize_color(raw_color: str, raw_name: str = "") -> str:
    """Map raw color string to one of our 12 colors."""
    text = raw_color.lower().strip()

    # Direct lookup
    if text in COLOR_MAP:
        return COLOR_MAP[text]

    # Try each key as substring
    for key, value in sorted(COLOR_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if key in text:
            return value

    # Fallback: try product name
    name_lower = raw_name.lower()
    for key, value in sorted(COLOR_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if key in name_lower:
            return value

    return "black"  # Safe default


def normalize_style(raw_name: str, category: str = "") -> str:
    """Infer style from product name and category."""
    text = f"{raw_name} {category}".lower()

    for key, value in STYLE_MAP.items():
        if key in text:
            return value

    # Category-based defaults
    if category in ("Dress", "Coat", "Heels", "Shirt"):
        return "formal"
    if category in ("Sneakers", "Shorts", "Hoodie"):
        return "sporty" if category == "Sneakers" else "casual"

    return DEFAULT_STYLE


def parse_price(raw_price: str) -> int | None:
    """Extract integer CAD price from string like '$49.95' or 'CAD 120.00'."""
    if not raw_price:
        return None

    # Remove currency symbols and non-numeric chars except dots
    cleaned = re.sub(r"[^\d.]", "", raw_price.strip())
    if not cleaned:
        return None

    try:
        return round(float(cleaned))
    except ValueError:
        return None


def normalize_product(raw: dict, brand: str) -> dict | None:
    """
    Normalize a raw scraped product dict into the products table schema.

    Required raw keys: name, price, image_url
    Optional raw keys: color, category_hint, affiliate_url

    Returns None if the product can't be categorized.
    """
    name = raw.get("name", "").strip()
    if not name:
        return None

    category = normalize_category(name, raw.get("category_hint", ""))
    if category is None:
        return None

    price = parse_price(raw.get("price", ""))
    if price is None or price < 5 or price > 500:
        return None

    image_url = raw.get("image_url", "").strip()
    if not image_url:
        return None

    # Ensure absolute URL
    if image_url.startswith("//"):
        image_url = "https:" + image_url

    color = normalize_color(raw.get("color", ""), name)
    style = normalize_style(name, category)

    return {
        "name": name,
        "brand": brand.upper(),
        "category": category,
        "color": color,
        "style": style,
        "price": price,
        "image_url": image_url,
        "affiliate_url": raw.get("affiliate_url"),
    }
