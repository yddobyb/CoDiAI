#!/usr/bin/env python3
"""
Embedding generator for products without embeddings.

Queries Supabase for products where embedding IS NULL, generates CLIP ViT-B/32
embeddings from product images, and uploads them back to pgvector.

Usage:
    python embed_products.py              # Process all un-embedded products
    python embed_products.py --batch 32   # Custom batch size
    python embed_products.py --dry-run    # Preview without uploading

Requirements:
    pip install open-clip-torch pillow requests supabase tqdm
"""

import argparse
import hashlib
import os
import time

import numpy as np
import open_clip
import requests
import torch
from io import BytesIO
from PIL import Image
from supabase import create_client
from tqdm import tqdm

ARITZIA_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "scraper", "aritzia_cache"
)

# ── Config ──
SUPABASE_URL = "https://REMOVED_PROJECT_ID.supabase.co"
SUPABASE_KEY = (
    "***REMOVED_JWT_HEADER***."
    "***REMOVED_JWT_PAYLOAD***."
    "***REMOVED_JWT_SIG***"
)
CLIP_MODEL = "ViT-B-32"
CLIP_PRETRAINED = "openai"
EMBEDDING_DIM = 512
IMAGE_TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def load_clip():
    """Load CLIP model and preprocessing."""
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(
        CLIP_MODEL, pretrained=CLIP_PRETRAINED
    )
    model = model.to(device).eval()
    print(f"CLIP {CLIP_MODEL} loaded on {device}")
    return model, preprocess, device


def download_image(url: str) -> Image.Image | None:
    """Download image from URL and return as PIL Image. Checks Aritzia local cache first."""
    if "assets.aritzia.com" in url:
        cache_key = hashlib.md5(url.encode()).hexdigest()[:16]
        cache_path = os.path.join(ARITZIA_CACHE_DIR, f"{cache_key}.jpg")
        if os.path.exists(cache_path):
            try:
                return Image.open(cache_path).convert("RGB")
            except Exception:
                pass
    try:
        resp = requests.get(url, headers=HEADERS, timeout=IMAGE_TIMEOUT)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGB")
    except Exception:
        return None


def generate_embedding(
    image: Image.Image, model, preprocess, device
) -> np.ndarray:
    """Generate L2-normalized 512D CLIP embedding from a PIL image."""
    img_tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(img_tensor)
        emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy().flatten()


def fetch_unembedded(client) -> list[dict]:
    """Fetch all products that don't have an embedding yet."""
    products = []
    page = 0
    while True:
        resp = (
            client.table("products")
            .select("id, name, brand, category, image_url")
            .is_("embedding", "null")
            .range(page * 1000, (page + 1) * 1000 - 1)
            .execute()
        )
        if not resp.data:
            break
        products.extend(resp.data)
        page += 1
    return products


def main():
    parser = argparse.ArgumentParser(description="Generate CLIP embeddings for products")
    parser.add_argument("--batch", type=int, default=16, help="Batch size for processing")
    parser.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    args = parser.parse_args()

    # Connect to Supabase
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch products needing embeddings
    products = fetch_unembedded(client)
    print(f"Products without embeddings: {len(products)}")

    if not products:
        print("All products already have embeddings. Nothing to do.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would process {len(products)} products:")
        for p in products[:5]:
            print(f"  - {p['name']} ({p['brand']}, {p['category']})")
        if len(products) > 5:
            print(f"  ... and {len(products) - 5} more")
        return

    # Load CLIP
    model, preprocess, device = load_clip()

    # Process
    success = 0
    failed = 0

    for product in tqdm(products, desc="Generating embeddings"):
        img = download_image(product["image_url"])
        if img is None:
            failed += 1
            continue

        emb = generate_embedding(img, model, preprocess, device)

        try:
            client.table("products").update(
                {"embedding": emb.tolist()}
            ).eq("id", product["id"]).execute()
            success += 1
        except Exception as e:
            failed += 1
            if failed <= 3:
                print(f"\n  Upload error [{product['id']}]: {e}")

        # Rate limiting
        if (success + failed) % 50 == 0:
            time.sleep(1)

    print(f"\nDone! {success} embeddings generated, {failed} failed.")

    # Save backup
    if success > 0:
        import os
        save_dir = os.path.expanduser(
            "~/Documents/personal_project/codi/model/saved_model"
        )
        backup_path = os.path.join(save_dir, "product_embeddings.npz")
        if os.path.exists(backup_path):
            print(f"Note: Existing backup at {backup_path} — re-run notebook cell 7 to update.")


if __name__ == "__main__":
    main()
