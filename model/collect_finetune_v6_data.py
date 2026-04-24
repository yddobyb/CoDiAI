#!/usr/bin/env python3
"""
Collect training images for v6 fine-tune (targeted category improvement).

Target classes with known v5 weaknesses:
  - Flats / Heels  (Steve Madden studio-side — heavy augmentation required)
  - Jacket / Hoodie (Aritzia + Oak+Fort on-body preferred)

Writes:
  model/data/finetune_v6/{Flats,Heels,Jacket,Hoodie}/  — downloaded JPGs
  model/data/finetune_v6/manifest.json                 — {category, url, path, brand, color, source}

Re-run safe: skips files that already exist locally.
"""

import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "scraper"))
from config import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

from supabase import create_client  # noqa: E402

OUT_DIR = Path(__file__).parent / "data" / "finetune_v6"
OUT_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_PATH = OUT_DIR / "manifest.json"

TARGETS = [
    # (label, brand, category_in_db, extra_filter_desc)
    ("Flats",   "STEVE MADDEN", "Flats",   None),
    ("Heels",   "STEVE MADDEN", "Heels",   None),
    # Aritzia on-body shots end in `_on_a` in the Cloudinary URL.
    ("Jacket",  "ARITZIA",      "Jacket",  "on_body"),
    ("Hoodie",  "ARITZIA",      "Hoodie",  "on_body"),
    ("Coat",    "ARITZIA",      "Coat",    "on_body"),
    ("Sweater", "ARITZIA",      "Sweater", "on_body"),
    ("Jacket",  "OAK + FORT",   "Jacket",  None),
    ("Hoodie",  "OAK + FORT",   "Hoodie",  None),
    ("Coat",    "OAK + FORT",   "Coat",    None),
    ("Sweater", "OAK + FORT",   "Sweater", None),
    # v6c: broaden Hoodie — only 100 Kaggle samples + 16 DB on-body was too few.
    # Catalog-style shots included; augmentation (rotate/zoom) bridges domain gap.
    ("Hoodie",  "LULULEMON",    "Hoodie",  None),
    ("Hoodie",  "GARAGE",       "Hoodie",  None),
    ("Hoodie",  "ZARA",         "Hoodie",  None),
    ("Hoodie",  "UNIQLO",       "Hoodie",  None),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def fetch_rows(client, brand: str, category: str, on_body: bool) -> list[dict]:
    """Page through products for a brand+category; optionally filter Aritzia on-body."""
    rows: list[dict] = []
    page = 0
    while True:
        q = (
            client.table("products")
            .select("name, color, image_url")
            .eq("brand", brand)
            .eq("category", category)
            .range(page * 1000, (page + 1) * 1000 - 1)
        )
        resp = q.execute()
        if not resp.data:
            break
        rows.extend(resp.data)
        if len(resp.data) < 1000:
            break
        page += 1
    if on_body:
        # Aritzia on-body shots contain `_on_a` or `/on_a/` pattern before the transform
        rows = [r for r in rows if "_on_a" in r["image_url"] or "/on_a/" in r["image_url"]]
    return rows


def image_filename(url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:16]
    return f"{h}.jpg"


def download(url: str, dst: Path) -> bool:
    if dst.exists() and dst.stat().st_size > 1024:
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        dst.write_bytes(r.content)
        return dst.stat().st_size > 1024
    except Exception as e:
        print(f"  ✗ {url[:80]}: {e}")
        if dst.exists():
            dst.unlink()
        return False


def main():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    manifest: list[dict] = []
    for label, brand, category, extra in TARGETS:
        on_body = extra == "on_body"
        rows = fetch_rows(client, brand, category, on_body)
        print(f"  {brand:12s} {category:8s} {'on-body' if on_body else 'all     '} → {len(rows)}")
        cat_dir = OUT_DIR / label
        cat_dir.mkdir(exist_ok=True)
        for r in rows:
            url = r["image_url"]
            path = cat_dir / image_filename(url)
            manifest.append({
                "label": label,
                "brand": brand,
                "db_category": category,
                "color": r.get("color", ""),
                "url": url,
                "path": str(path.relative_to(OUT_DIR.parent.parent)),
                "source": "on_body" if on_body else "catalog",
            })

    print(f"\n→ {len(manifest)} target images; downloading with 8 workers…")
    skipped = downloaded = failed = 0

    def task(entry):
        url = entry["url"]
        dst = OUT_DIR.parent.parent / entry["path"]
        existed = dst.exists() and dst.stat().st_size > 1024
        ok = download(url, dst)
        return existed, ok

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(task, e) for e in manifest]
        for i, f in enumerate(as_completed(futures), 1):
            existed, ok = f.result()
            if existed:
                skipped += 1
            elif ok:
                downloaded += 1
            else:
                failed += 1
            if i % 100 == 0:
                print(f"  …{i}/{len(manifest)}  (new={downloaded} skip={skipped} fail={failed})")

    # Filter out failures from manifest
    manifest_ok = [e for e in manifest if (OUT_DIR.parent.parent / e["path"]).exists() and (OUT_DIR.parent.parent / e["path"]).stat().st_size > 1024]
    MANIFEST_PATH.write_text(json.dumps(manifest_ok, indent=2, ensure_ascii=False))

    print(f"\n✓ skipped={skipped} downloaded={downloaded} failed={failed}")
    print(f"  manifest: {MANIFEST_PATH} ({len(manifest_ok)} usable)")

    # Summary by label
    from collections import Counter
    by_label = Counter(e["label"] for e in manifest_ok)
    print(f"  by label: {dict(by_label)}")


if __name__ == "__main__":
    main()
