"""
Playwright-based scraper for JS-rendered / bot-blocked clothing sites.

Uses page-load + network-interception to capture product data from XHR
responses (most modern sites call an internal JSON API — Algolia, Shopify,
Salesforce — that returns full structured data). This is much more robust
than DOM scraping of CSS-hashed class names.

Usage:
    python playwright_scraper.py aritzia shoes "https://www.aritzia.com/us/en/clothing/shoes"
    python playwright_scraper.py aritzia coats "https://www.aritzia.com/us/en/clothing/coats-and-jackets"
    python playwright_scraper.py lululemon shoes "https://shop.lululemon.com/c/womens-shoes/_/N-1z12t9p"
    python playwright_scraper.py garage dresses "https://www.garageclothing.com/ca/women/clothing/dresses"
    python playwright_scraper.py dynamite jeans "https://www.dynamiteclothing.com/ca/jeans"
"""

import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


# ---- brand-specific response parsers ----
# Each parser takes the raw JSON body of a captured XHR response and
# returns a list[dict] of normalized products, or [] if not relevant.


def parse_aritzia(body: dict) -> list[dict]:
    """Algolia multi-index query: { results: [{ hits: [...] }] } or { hits: [...] }."""
    hits = []
    if isinstance(body, dict):
        if "results" in body:
            for r in body.get("results", []):
                hits.extend(r.get("hits", []))
        elif "hits" in body:
            hits = body["hits"]
    out = []
    for h in hits:
        if not isinstance(h, dict):
            continue
        price_obj = h.get("price") or {}
        price = price_obj.get("min") if isinstance(price_obj, dict) else price_obj
        slug = h.get("slug") or h.get("url") or ""
        if not slug or price is None:
            continue
        if slug.startswith("/"):
            product_url = f"https://www.aritzia.com/us/en/product{slug}"
        elif slug.startswith("http"):
            product_url = slug
        else:
            product_url = f"https://www.aritzia.com/us/en/product/{slug}"
        img = h.get("defaultImage") or ""
        if img and not img.startswith("http"):
            img = f"https://assets.aritzia.com/image/upload/f_auto,q_auto/{img}"
        color = ""
        if isinstance(h.get("color"), dict):
            color = h["color"].get("name") or h["color"].get("value") or ""
        elif isinstance(h.get("color"), list) and h["color"]:
            first = h["color"][0]
            color = first.get("name") if isinstance(first, dict) else str(first)
        elif isinstance(h.get("color"), str):
            color = h["color"]
        out.append({
            "name": h.get("name") or h.get("displayName") or "",
            "price": float(price),
            "image_url": img,
            "product_url": product_url,
            "color": color,
            "category_hint": (h.get("hierarchicalCategories") or {}).get("lvl1", "") if isinstance(h.get("hierarchicalCategories"), dict) else "",
        })
    return out


def parse_lululemon(body: dict) -> list[dict]:
    """Lululemon uses Adobe/Endeca-style. Look for records array."""
    records = []
    if isinstance(body, dict):
        if "records" in body:
            records = body["records"]
        elif "plpResults" in body:
            records = body["plpResults"].get("records", [])
        elif "hits" in body:
            records = body["hits"]
    out = []
    for r in records:
        if not isinstance(r, dict):
            continue
        attrs = r.get("attributes") or r
        name = (attrs.get("product.displayName") or attrs.get("name") or [""])
        name = name[0] if isinstance(name, list) else name
        price = attrs.get("product.price") or attrs.get("price") or [0]
        price = price[0] if isinstance(price, list) else price
        try:
            price = float(str(price).replace("$", "").replace(",", ""))
        except Exception:
            continue
        img = attrs.get("product.media.image") or attrs.get("image") or [""]
        img = img[0] if isinstance(img, list) else img
        url = attrs.get("product.url") or attrs.get("url") or [""]
        url = url[0] if isinstance(url, list) else url
        if not name or not url or not img:
            continue
        if url.startswith("/"):
            url = "https://shop.lululemon.com" + url
        out.append({
            "name": name,
            "price": price,
            "image_url": img,
            "product_url": url,
            "color": "",
        })
    return out


def parse_shopify(body: dict) -> list[dict]:
    """Shopify /products.json or /collections/X/products.json endpoint."""
    products = body.get("products", []) if isinstance(body, dict) else []
    out = []
    for p in products:
        if not isinstance(p, dict):
            continue
        variants = p.get("variants", [])
        if not variants:
            continue
        price = float(variants[0].get("price", 0) or 0)
        if price <= 0:
            continue
        images = p.get("images", [])
        img = images[0].get("src") if images else ""
        handle = p.get("handle", "")
        if not img or not handle:
            continue
        out.append({
            "name": p.get("title", ""),
            "price": price,
            "image_url": img,
            "product_url": f"/products/{handle}",
            "color": "",
        })
    return out


PARSERS = {
    "aritzia": parse_aritzia,
    "lululemon": parse_lululemon,
    "garage": parse_shopify,
    "dynamite": parse_shopify,
}

API_FILTERS = {
    "aritzia": lambda url: "search-1.aritzia.com" in url or "algolia" in url,
    "lululemon": lambda url: ("shop.lululemon.com" in url and ("plpResults" in url or "products" in url or "catalog" in url)),
    "garage": lambda url: "products.json" in url or "search?q=" in url,
    "dynamite": lambda url: "products.json" in url or "search?q=" in url,
}


def scrape(brand: str, category: str, url: str, max_scrolls: int = 25, headful: bool = False):
    parser = PARSERS.get(brand)
    url_filter = API_FILTERS.get(brand)
    if not parser or not url_filter:
        print(f"No parser for brand '{brand}'.", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not headful,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1400, "height": 900},
            locale="en-CA",
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = ctx.new_page()

        seen_urls = set()
        all_products: list[dict] = []
        seen_product_keys = set()

        def on_response(resp):
            try:
                if not url_filter(resp.url):
                    return
                if resp.url in seen_urls:
                    return
                body = resp.json()
            except Exception:
                return
            seen_urls.add(resp.url)
            parsed = parser(body)
            for p_ in parsed:
                key = p_.get("product_url") or p_.get("name")
                if key and key not in seen_product_keys:
                    seen_product_keys.add(key)
                    all_products.append(p_)

        page.on("response", on_response)

        print(f"→ Navigating {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        prev = 0
        stable = 0
        for i in range(max_scrolls):
            page.evaluate("window.scrollBy(0, window.innerHeight * 1.2)")
            page.wait_for_timeout(1500)
            count = len(all_products)
            print(f"  scroll {i + 1}/{max_scrolls} → {count} products captured")
            if count == prev:
                stable += 1
                if stable >= 5:
                    break
            else:
                stable = 0
            prev = count

        # Try clicking "Load more" / "Show more" button if present
        try:
            btn = page.locator("button:has-text('View More'), button:has-text('Load More'), button:has-text('Show More'), a:has-text('View More')").first
            for _ in range(5):
                if btn.count() and btn.is_visible():
                    btn.click(timeout=2000)
                    page.wait_for_timeout(1800)
                else:
                    break
        except Exception:
            pass

        browser.close()

    # Enrich with relative-to-absolute URLs for shopify-style brands
    if brand in ("garage", "dynamite"):
        domain = {"garage": "https://www.garageclothing.com", "dynamite": "https://www.dynamiteclothing.com"}[brand]
        for p_ in all_products:
            if p_["product_url"].startswith("/"):
                p_["product_url"] = domain + p_["product_url"]

    out_path = Path("/tmp") / f"{brand}_{category}.json"
    out_path.write_text(json.dumps(all_products, indent=2, ensure_ascii=False))
    print(f"\n✓ Saved {len(all_products)} products → {out_path}")
    if all_products:
        print(f"  sample: {all_products[0]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brand", choices=list(PARSERS.keys()))
    ap.add_argument("category")
    ap.add_argument("url")
    ap.add_argument("--max-scrolls", type=int, default=25)
    ap.add_argument("--headful", action="store_true", help="Show browser UI")
    args = ap.parse_args()
    scrape(args.brand, args.category, args.url, args.max_scrolls, args.headful)


if __name__ == "__main__":
    main()
