"""
Brand-specific configuration for product scraping.

Each brand entry defines:
  - base_url: starting point for crawling
  - categories: URL patterns per product category
  - selectors: CSS selectors for extracting product data
  - gender_filter: filter keyword to limit to women's products
"""

# ── Supabase ──
# Load from environment — never hardcode keys. Set via shell:
#   export SUPABASE_URL="https://<project>.supabase.co"
#   export SUPABASE_KEY="<anon-or-service-role-key>"
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL / SUPABASE_KEY environment variables. "
        "Set them before running scraper scripts."
    )

# ── Rate limiting ──
REQUEST_DELAY = 1.5  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 15

# ── Category mapping (site-specific → our 15 categories) ──
CATEGORY_MAP = {
    # Tops
    "t-shirt": "T-shirt", "tee": "T-shirt", "t shirt": "T-shirt",
    "tank": "T-shirt", "cami": "T-shirt", "bodysuit": "T-shirt",
    "shirt": "Shirt", "blouse": "Shirt", "button": "Shirt",
    "hoodie": "Hoodie", "sweatshirt": "Hoodie",
    "sweater": "Sweater", "cardigan": "Sweater", "knit": "Sweater",
    "pullover": "Sweater", "turtleneck": "Sweater",
    # Bottoms
    "jeans": "Jeans", "denim": "Jeans",
    "pants": "Pants", "trouser": "Pants", "legging": "Pants",
    "jogger": "Pants", "chino": "Pants", "wide leg": "Pants",
    "shorts": "Shorts",
    "skirt": "Skirt",
    "dress": "Dress",
    # Outerwear
    "jacket": "Jacket", "blazer": "Jacket", "bomber": "Jacket",
    "vest": "Jacket", "puffer": "Jacket",
    "coat": "Coat", "trench": "Coat", "overcoat": "Coat", "parka": "Coat",
    # Shoes
    "sneaker": "Sneakers", "trainer": "Sneakers", "running": "Sneakers",
    "boot": "Boots", "chelsea": "Boots", "ankle boot": "Boots",
    "flat": "Flats", "loafer": "Flats", "ballet": "Flats",
    "mule": "Flats", "sandal": "Flats",
    "heel": "Heels", "pump": "Heels", "stiletto": "Heels",
    "mule heel": "Heels",
}

# ── Color mapping (site-specific → our 12 colors) ──
COLOR_MAP = {
    "black": "black", "noir": "black", "jet": "black", "onyx": "black",
    "white": "white", "ivory": "white", "cream": "white", "ecru": "white",
    "off-white": "white", "snow": "white", "chalk": "white",
    "gray": "gray", "grey": "gray", "charcoal": "gray", "heather": "gray",
    "silver": "gray", "slate": "gray",
    "beige": "beige", "tan": "beige", "sand": "beige", "camel": "beige",
    "khaki": "beige", "nude": "beige", "oat": "beige", "taupe": "beige",
    "bone": "beige", "natural": "beige",
    "brown": "brown", "chocolate": "brown", "coffee": "brown",
    "espresso": "brown", "mocha": "brown", "walnut": "brown",
    "navy": "navy", "midnight": "navy", "dark blue": "navy",
    "blue": "blue", "cobalt": "blue", "sky": "blue", "denim": "blue",
    "teal": "blue", "ocean": "blue", "azure": "blue", "indigo": "blue",
    "green": "green", "olive": "green", "sage": "green", "forest": "green",
    "emerald": "green", "moss": "green", "army": "green", "mint": "green",
    "hunter": "green", "khaki green": "green",
    "red": "red", "crimson": "red", "scarlet": "red", "burgundy": "red",
    "wine": "red", "cherry": "red", "rust": "red", "brick": "red",
    "maroon": "red", "berry": "red",
    "pink": "pink", "rose": "pink", "blush": "pink", "coral": "pink",
    "salmon": "pink", "fuchsia": "pink", "mauve": "pink",
    "dusty rose": "pink", "hot pink": "pink",
    "yellow": "yellow", "gold": "yellow", "mustard": "yellow",
    "lemon": "yellow", "honey": "yellow", "amber": "yellow",
    "purple": "purple", "plum": "purple", "lavender": "purple",
    "lilac": "purple", "violet": "purple", "eggplant": "purple",
}

# ── Style mapping ──
STYLE_MAP = {
    "casual": "casual", "everyday": "casual", "relaxed": "casual",
    "basic": "casual", "lounge": "casual", "weekend": "casual",
    "formal": "formal", "office": "formal", "work": "formal",
    "dress": "formal", "business": "formal", "tailored": "formal",
    "sporty": "sporty", "athletic": "sporty", "active": "sporty",
    "sport": "sporty", "performance": "sporty", "training": "sporty",
}
DEFAULT_STYLE = "casual"

# ── Brand configurations ──
BRANDS = {
    "GARAGE": {
        "base_url": "https://www.garageclothing.com",
        "sitemap_url": "https://www.garageclothing.com/sitemap.xml",
        "categories": {
            "Tops": "/ca/c/tops",
            "Bottoms": "/ca/c/bottoms",
            "Jeans": "/ca/c/jeans",
            "Dresses": "/ca/c/dresses",
            "Outerwear": "/ca/c/jackets-coats",
        },
        "selectors": {
            "product_link": "a.product-card__link",
            "name": "h1.product-name",
            "price": "span.product-price__value",
            "color": "span.swatch__label",
            "image": "img.product-image__img",
            "category_hint": "nav.breadcrumb li:last-child",
        },
    },
    "DYNAMITE": {
        "base_url": "https://www.dynamiteclothing.com",
        "categories": {
            "Tops": "/ca/c/tops",
            "Bottoms": "/ca/c/bottoms",
            "Jeans": "/ca/c/jeans",
            "Dresses": "/ca/c/dresses",
            "Outerwear": "/ca/c/jackets-blazers",
        },
        "selectors": {
            "product_link": "a.product-card__link",
            "name": "h1.product-name",
            "price": "span.product-price__value",
            "color": "span.swatch__label",
            "image": "img.product-image__img",
            "category_hint": "nav.breadcrumb li:last-child",
        },
    },
    "COS": {
        "base_url": "https://www.cos.com",
        "categories": {
            "Tops": "/en_cad/women/tops.html",
            "Bottoms": "/en_cad/women/trousers.html",
            "Jeans": "/en_cad/women/jeans.html",
            "Dresses": "/en_cad/women/dresses.html",
            "Outerwear": "/en_cad/women/coats-jackets.html",
            "Knitwear": "/en_cad/women/knitwear.html",
            "Shoes": "/en_cad/women/shoes.html",
        },
        "selectors": {
            "product_link": "a.product-card-link",
            "name": "h1.product-detail-title",
            "price": "span.product-price",
            "color": ".product-detail-colour-name",
            "image": "img.product-detail-image",
            "category_hint": ".breadcrumb__item--current",
        },
    },
    "SIMONS": {
        "base_url": "https://www.simons.ca",
        "categories": {
            "Tops": "/en/women-clothing/blouses-shirts--6670",
            "T-shirts": "/en/women-clothing/t-shirts-tops--6669",
            "Bottoms": "/en/women-clothing/pants--6672",
            "Jeans": "/en/women-clothing/jeans--6671",
            "Dresses": "/en/women-clothing/dresses--6668",
            "Outerwear": "/en/women-clothing/coats-jackets--6661",
            "Sweaters": "/en/women-clothing/sweaters-cardigans--6676",
        },
        "selectors": {
            "product_link": "a.product-tile__link",
            "name": "h1.product-name",
            "price": ".product-price .value",
            "color": ".color-swatch__label",
            "image": "img.product-tile__image",
            "category_hint": ".breadcrumb-item:last-child",
        },
    },
    "LULULEMON": {
        "base_url": "https://shop.lululemon.com",
        "categories": {
            "Tops": "/c/women-tops/_/N-1z13zi2Z7vf",
            "Bottoms": "/c/women-pants/_/N-8r6Z1z0xcmk",
            "Shorts": "/c/women-shorts/_/N-8s1",
            "Outerwear": "/c/women-coats-and-jackets/_/N-8q3",
            "Dresses": "/c/women-dresses/_/N-8r2",
        },
        "selectors": {
            "product_link": "a.product-tile__link",
            "name": "h1.product-title",
            "price": "span.price-1jnQj",
            "color": ".color-swatch__label",
            "image": "img.product-tile__image",
            "category_hint": ".breadcrumb li:last-child",
        },
    },
    "FRANK AND OAK": {
        "base_url": "https://ca.frankandoak.com",
        "categories": {
            "Tops": "/collections/womens-tops",
            "Bottoms": "/collections/womens-bottoms",
            "Dresses": "/collections/womens-dresses",
            "Outerwear": "/collections/womens-outerwear",
            "Sweaters": "/collections/womens-sweaters",
        },
        "selectors": {
            "product_link": ".product-card a",
            "name": "h1.product-single__title",
            "price": "span.product__price",
            "color": ".swatch__label",
            "image": "img.product-featured-img",
            "category_hint": ".breadcrumb li:last-child",
        },
    },
}
