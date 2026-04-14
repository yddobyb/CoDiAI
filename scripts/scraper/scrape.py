"""
Product scraper using requests + BeautifulSoup.

Scrapes product listing pages → collects product URLs → scrapes individual
product pages for details (name, price, color, image).

Usage:
    from scrape import scrape_brand
    products = scrape_brand("GARAGE", max_products=50)
"""

import time
import requests
from bs4 import BeautifulSoup
from config import BRANDS, REQUEST_DELAY, MAX_RETRIES, TIMEOUT

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
}


def _get(url: str) -> BeautifulSoup | None:
    """Fetch URL with retries and return parsed soup."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            print(f"  [Retry {attempt + 1}/{MAX_RETRIES}] {url}: {e}")
            time.sleep(REQUEST_DELAY * (attempt + 1))
    return None


def _extract_product_links(soup: BeautifulSoup, selector: str, base_url: str) -> list[str]:
    """Extract product detail page URLs from a listing page."""
    links = []
    for el in soup.select(selector):
        href = el.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = base_url + href
        if href not in links:
            links.append(href)
    return links


def _extract_text(soup: BeautifulSoup, selector: str) -> str:
    """Safe text extraction from a CSS selector."""
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else ""


def _extract_image(soup: BeautifulSoup, selector: str) -> str:
    """Extract image URL from img tag (src or data-src)."""
    el = soup.select_one(selector)
    if not el:
        return ""
    return el.get("src") or el.get("data-src") or el.get("data-lazy-src") or ""


def scrape_product_page(url: str, selectors: dict) -> dict | None:
    """Scrape a single product detail page."""
    soup = _get(url)
    if soup is None:
        return None

    name = _extract_text(soup, selectors["name"])
    if not name:
        return None

    return {
        "name": name,
        "price": _extract_text(soup, selectors["price"]),
        "color": _extract_text(soup, selectors.get("color", "")),
        "image_url": _extract_image(soup, selectors["image"]),
        "category_hint": _extract_text(soup, selectors.get("category_hint", "")),
        "affiliate_url": url,
    }


def scrape_brand(brand_key: str, max_products: int = 60) -> list[dict]:
    """
    Scrape products for a brand.

    Args:
        brand_key: Key from BRANDS config (e.g. "GARAGE")
        max_products: Maximum products to scrape across all categories

    Returns:
        List of raw product dicts (not yet normalized)
    """
    cfg = BRANDS.get(brand_key)
    if cfg is None:
        print(f"Unknown brand: {brand_key}")
        return []

    base_url = cfg["base_url"]
    selectors = cfg["selectors"]
    products = []

    per_category = max(max_products // len(cfg["categories"]), 5)

    print(f"\n{'='*50}")
    print(f"Scraping {brand_key} (max {max_products} products)")
    print(f"{'='*50}")

    for cat_name, cat_path in cfg["categories"].items():
        if len(products) >= max_products:
            break

        url = base_url + cat_path
        print(f"\n  [{cat_name}] {url}")

        soup = _get(url)
        if soup is None:
            print(f"  ✗ Failed to load listing page")
            continue

        links = _extract_product_links(soup, selectors["product_link"], base_url)
        print(f"  Found {len(links)} product links")

        for link in links[:per_category]:
            if len(products) >= max_products:
                break

            time.sleep(REQUEST_DELAY)
            product = scrape_product_page(link, selectors)

            if product and product.get("name") and product.get("image_url"):
                product["category_hint"] = f"{cat_name} {product.get('category_hint', '')}"
                products.append(product)
                print(f"    + {product['name'][:50]}")
            else:
                print(f"    ✗ Skipped: {link[:60]}")

    print(f"\n  Total: {len(products)} products scraped for {brand_key}")
    return products
