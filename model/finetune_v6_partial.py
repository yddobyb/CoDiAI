"""
Fashion Codi AI v6 — Targeted partial fine-tune on top of v5.

Fixes known v5 weaknesses:
  - Flats ↔ Heels confusion         → add 803 + 789 Steve Madden shoes
  - Jacket / Hoodie low accuracy    → add 150 on-body Aritzia + Oak+Fort samples
  - Coat / Sweater                  → strengthened with Aritzia on-body + Oak+Fort

Strategy:
  1. Reproduce v5's exact train/val/test split (random_state=42) so we can
     compare head-to-head on the SAME test set.
  2. Load v5's fashion_v5_multitask.keras.
  3. Freeze everything except: last 5 MobileNetV2 layers + shared_dense +
     category-head + color-hidden + color-head. Season head stays frozen.
  4. Append DB images to train split only — never contaminate test.
     Season label for DB samples is inferred (Jacket/Coat/Hoodie/Sweater→fall,
     Flats/Heels→spring) but weighted 0 in the loss so it doesn't pull the
     season head.
  5. Heavier augmentation for DB samples (rotation + perspective) to combat
     the studio-vs-user-photo domain shift.
  6. Low LR (1e-5) + 6 epochs.

Outputs:
  saved_model/fashion_v6_multitask.keras
  saved_model/training_results_v6.json
  tflite/fashion_multitask_v6.tflite
  Copies TFLite + labels to app/assets (same filenames v5 used, so the Flutter
  app picks it up automatically).
"""
import json
import os
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split

IMG_SIZE = 224
BATCH_SIZE = 32
MAX_PER_CLASS = 1500
EPOCHS = 6
LR = 1e-5

# v6c: same skip policy as v6b (no shoes), but with expanded Hoodie data:
# v6b had only 16 Hoodie DB samples → no movement. v6c adds LULULEMON(34) +
# GARAGE(12) + ZARA(5) + UNIQLO(1) catalog shots, Hoodie total 16 → 68.
SKIP_LABELS: set[str] = {"Flats", "Heels"}
VARIANT = "v6c"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = BASE_DIR / "saved_model"
TFLITE_DIR = BASE_DIR / "tflite"
FLUTTER_ASSETS = BASE_DIR.parent / "app" / "assets"
FINETUNE_DIR = DATA_DIR / "finetune_v6"
V5_MODEL = SAVE_DIR / "fashion_v5_multitask.keras"

# ── v5 mappings (copied verbatim so the split matches bit-for-bit) ──
ARTICLE_TO_CATEGORY = {
    'Tshirts': 'T-shirt', 'Tops': 'T-shirt', 'Shirts': 'Shirt',
    'Hoodie': 'Hoodie', 'Sweatshirts': 'Sweater', 'Sweaters': 'Sweater',
    'Jackets': 'Jacket', 'Blazer': 'Jacket', 'Blazers': 'Jacket',
    'Outwear': 'Coat',
    'Jeans': 'Jeans', 'Trousers': 'Pants', 'Track Pants': 'Pants',
    'Shorts': 'Shorts', 'Skirt': 'Skirt', 'Skirts': 'Skirt',
    'Dress': 'Dress', 'Dresses': 'Dress', 'Jumpsuit': 'Dress',
    'Sports Shoes': 'Sneakers', 'Casual Shoes': 'Sneakers',
    'Formal Shoes': 'Boots', 'Flats': 'Flats', 'Heels': 'Heels',
}
COLOUR_TO_COLOR = {
    'Black': 'black', 'White': 'white', 'Cream': 'white', 'Off White': 'white',
    'Grey': 'gray', 'Grey Melange': 'gray', 'Silver': 'gray',
    'Charcoal': 'gray', 'Steel': 'gray',
    'Navy Blue': 'navy',
    'Blue': 'blue', 'Turquoise Blue': 'blue', 'Teal': 'blue', 'Sea Green': 'blue',
    'Red': 'red', 'Maroon': 'red', 'Burgundy': 'red', 'Wine': 'red', 'Rust': 'red',
    'Pink': 'pink', 'Magenta': 'pink', 'Rose': 'pink', 'Peach': 'pink',
    'Mauve': 'pink', 'Lavender': 'pink', 'Fluorescent Green': 'green',
    'Brown': 'brown', 'Tan': 'brown', 'Copper': 'brown',
    'Coffee Brown': 'brown', 'Mushroom Brown': 'brown', 'Taupe': 'brown',
    'Beige': 'beige', 'Khaki': 'beige', 'Nude': 'beige', 'Skin': 'beige',
    'Green': 'green', 'Olive': 'green', 'Lime Green': 'green',
    'Yellow': 'yellow', 'Mustard': 'yellow', 'Gold': 'yellow',
    'Purple': 'purple', 'Plum': 'purple', 'Violet': 'purple',
    'Unknown': 'black',
}
SEASON_MAP = {'Spring': 'spring', 'Summer': 'summer', 'Fall': 'fall', 'Winter': 'winter'}

# Category-based season fallback for DB products (v5 script doesn't see these,
# so we assign a plausible season and mask it in the loss)
DB_CAT_TO_SEASON = {
    "Flats": "spring", "Heels": "spring",
    "Jacket": "fall", "Coat": "winter",
    "Hoodie": "fall", "Sweater": "fall",
}

# DB color string → v5 color space (colors are already 1-word lowercase in DB)
DB_COLOR_TO_V5 = {
    "black": "black", "white": "white", "cream": "white", "ivory": "white",
    "gray": "gray", "grey": "gray", "charcoal": "gray", "silver": "gray",
    "navy": "navy",
    "blue": "blue", "denim": "blue", "teal": "blue",
    "red": "red", "burgundy": "red", "wine": "red", "rust": "red", "maroon": "red",
    "pink": "pink", "rose": "pink", "blush": "pink",
    "brown": "brown", "tan": "brown", "chocolate": "brown", "espresso": "brown",
    "camel": "beige", "beige": "beige", "nude": "beige", "khaki": "beige",
    "taupe": "beige", "sand": "beige", "bone": "beige", "oat": "beige",
    "green": "green", "olive": "green", "sage": "green",
    "yellow": "yellow", "gold": "yellow", "mustard": "yellow",
}


# ── Step 1: Rebuild v5's exact train/val/test split ──
print("=" * 60)
print("Step 1: Rebuilding v5 split (random_state=42)")
print("=" * 60)

df = pd.read_csv(DATA_DIR / "dataset_final.csv")
df["cat_label"] = df["articleType"].map(ARTICLE_TO_CATEGORY)
df = df.dropna(subset=["cat_label"])
df["color_label_12"] = df["baseColour"].map(COLOUR_TO_COLOR)
df = df.dropna(subset=["color_label_12"])
df["season_label"] = df["season"].map(SEASON_MAP)
df = df.dropna(subset=["season_label"])
df = df[df["image_path"].apply(os.path.exists)].reset_index(drop=True)

CATEGORIES = sorted(df["cat_label"].unique())
COLORS = sorted(df["color_label_12"].unique())
SEASONS = sorted(df["season_label"].unique())
NUM_CAT, NUM_COL, NUM_SEA = len(CATEGORIES), len(COLORS), len(SEASONS)
cat2idx = {l: i for i, l in enumerate(CATEGORIES)}
col2idx = {l: i for i, l in enumerate(COLORS)}
sea2idx = {l: i for i, l in enumerate(SEASONS)}
print(f"CATEGORIES ({NUM_CAT}): {CATEGORIES}")
print(f"COLORS ({NUM_COL}): {COLORS}")
print(f"SEASONS ({NUM_SEA}): {SEASONS}")

balanced_dfs = []
for cat in CATEGORIES:
    subset = df[df["cat_label"] == cat]
    if len(subset) > MAX_PER_CLASS:
        subset = subset.sample(n=MAX_PER_CLASS, random_state=42)
    balanced_dfs.append(subset)
balanced_df = pd.concat(balanced_dfs, ignore_index=True)

train_df, temp_df = train_test_split(
    balanced_df, test_size=0.3, stratify=balanced_df["cat_label"], random_state=42
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.5, stratify=temp_df["cat_label"], random_state=42
)
train_df = train_df.copy().reset_index(drop=True)
val_df = val_df.copy().reset_index(drop=True)
test_df = test_df.copy().reset_index(drop=True)
print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")


# ── Step 2: Load DB manifest and convert to v5 label space ──
print("\n" + "=" * 60)
print("Step 2: Loading DB manifest (finetune_v6/manifest.json)")
print("=" * 60)

manifest = json.loads((FINETUNE_DIR / "manifest.json").read_text())
print(f"Manifest entries: {len(manifest)}")

db_rows = []
skipped = 0
for e in manifest:
    label = e["label"]
    if label not in cat2idx or label in SKIP_LABELS:
        skipped += 1
        continue
    raw_color = (e.get("color") or "").strip().lower()
    # First word only for compound colors like "black multi"
    first = raw_color.split()[0] if raw_color else ""
    mapped_color = DB_COLOR_TO_V5.get(first) or DB_COLOR_TO_V5.get(raw_color) or "black"
    if mapped_color not in col2idx:
        mapped_color = "black"  # fallback
    path = BASE_DIR / e["path"]
    if not path.exists():
        skipped += 1
        continue
    season = DB_CAT_TO_SEASON[label]
    db_rows.append({
        "image_path": str(path),
        "cat_label": label,
        "color_label_12": mapped_color,
        "season_label": season,
        "is_db": 1.0,  # 1.0 → mask season loss; 0.0 for Kaggle data
        "brand": e["brand"],
    })
print(f"DB rows usable: {len(db_rows)} (skipped {skipped})")

db_df = pd.DataFrame(db_rows)
from_counter = Counter((r["cat_label"], r["brand"]) for r in db_rows)
for k, v in sorted(from_counter.items()):
    print(f"  {k[0]:8s} {k[1]:15s}: {v}")

# Also held-out DB test: small stratified split for sanity-check eval
db_train, db_test = train_test_split(
    db_df, test_size=0.15, stratify=db_df["cat_label"], random_state=42,
)
db_train = db_train.copy().reset_index(drop=True)
db_test = db_test.copy().reset_index(drop=True)
print(f"DB train: {len(db_train)}, DB test: {len(db_test)}")


# ── Step 3: Merge DB train into main train_df (tag is_db) ──
train_df["is_db"] = 0.0
train_df["brand"] = "kaggle"
full_train = pd.concat([train_df[["image_path", "cat_label", "color_label_12", "season_label", "is_db", "brand"]], db_train], ignore_index=True)
full_train["cat_idx"] = full_train["cat_label"].map(cat2idx)
full_train["col_idx"] = full_train["color_label_12"].map(col2idx)
full_train["sea_idx"] = full_train["season_label"].map(sea2idx)

val_df["cat_idx"] = val_df["cat_label"].map(cat2idx)
val_df["col_idx"] = val_df["color_label_12"].map(col2idx)
val_df["sea_idx"] = val_df["season_label"].map(sea2idx)
test_df["cat_idx"] = test_df["cat_label"].map(cat2idx)
test_df["col_idx"] = test_df["color_label_12"].map(col2idx)
test_df["sea_idx"] = test_df["season_label"].map(sea2idx)

db_test["cat_idx"] = db_test["cat_label"].map(cat2idx)
db_test["col_idx"] = db_test["color_label_12"].map(col2idx)
db_test["sea_idx"] = db_test["season_label"].map(sea2idx)

print(f"\nFull train: {len(full_train)} ({int(full_train['is_db'].sum())} from DB)")


# ── Step 4: tf.data pipelines ──
print("\n" + "=" * 60)
print("Step 4: Building data pipelines")
print("=" * 60)


def load_and_preprocess(image_path, cat_label, col_label, sea_label, is_db):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    return img, cat_label, col_label, sea_label, is_db


def rotate_image(image, max_deg):
    # Light per-sample rotation via small crop + re-resize (TF's built-in rotate
    # needs tfa; avoid the dependency by using random zoom + crop which
    # behaves like a mild perspective warp).
    scale = tf.random.uniform([], 1.0, 1.0 + max_deg / 30.0)
    h = tf.cast(tf.cast(IMG_SIZE, tf.float32) * scale, tf.int32)
    image = tf.image.resize(image, [h, h])
    return tf.image.random_crop(image, [IMG_SIZE, IMG_SIZE, 3])


def augment(image, cat_label, col_label, sea_label, is_db):
    # Base augmentation (same as v5)
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, 0.15)
    image = tf.image.random_contrast(image, 0.85, 1.15)
    padded = tf.image.resize(image, [IMG_SIZE + 20, IMG_SIZE + 20])
    image = tf.image.random_crop(padded, [IMG_SIZE, IMG_SIZE, 3])
    # Extra rotation/zoom for DB samples (studio → user-photo domain shift)
    image = tf.cond(
        tf.greater(is_db, 0.5),
        lambda: rotate_image(image, max_deg=15.0),
        lambda: image,
    )
    image = tf.clip_by_value(image, 0.0, 255.0)
    return image, cat_label, col_label, sea_label, is_db


def finalize(image, cat_label, col_label, sea_label, is_db):
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    # Season sample weight: 0.0 for DB, 1.0 for Kaggle
    sea_weight = 1.0 - is_db
    return (
        image,
        {"category": cat_label, "color": col_label, "season": sea_label},
        {"category": tf.ones([]), "color": tf.ones([]), "season": sea_weight},
    )


def make_dataset(dataframe, training=False, use_weights=True):
    paths = dataframe["image_path"].values
    cat_labels = tf.one_hot(dataframe["cat_idx"].values.astype(np.int32), NUM_CAT)
    col_labels = tf.one_hot(dataframe["col_idx"].values.astype(np.int32), NUM_COL)
    sea_labels = tf.one_hot(dataframe["sea_idx"].values.astype(np.int32), NUM_SEA)
    is_db = dataframe["is_db"].values.astype(np.float32) if "is_db" in dataframe.columns else np.zeros(len(dataframe), dtype=np.float32)

    ds = tf.data.Dataset.from_tensor_slices((paths, cat_labels, col_labels, sea_labels, is_db))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.shuffle(4096)
    if use_weights:
        ds = ds.map(finalize, num_parallel_calls=tf.data.AUTOTUNE)
    else:
        ds = ds.map(
            lambda im, c, co, s, d: (
                tf.keras.applications.mobilenet_v2.preprocess_input(im),
                {"category": c, "color": co, "season": s},
            ),
            num_parallel_calls=tf.data.AUTOTUNE,
        )
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


train_ds = make_dataset(full_train, training=True, use_weights=True)
val_ds = make_dataset(val_df, training=False, use_weights=False)
test_ds = make_dataset(test_df, training=False, use_weights=False)
db_test_ds = make_dataset(db_test, training=False, use_weights=False)


# ── Step 5: Load v5 and set up partial fine-tune ──
print("\n" + "=" * 60)
print("Step 5: Loading v5 and freezing layers")
print("=" * 60)

model = tf.keras.models.load_model(V5_MODEL)

# Freeze everything first, then unfreeze target heads + last few base layers
for layer in model.layers:
    layer.trainable = False

# Find the MobileNetV2 submodel (wrapped as a layer in v5)
mobilenet = None
for layer in model.layers:
    if isinstance(layer, tf.keras.Model):
        mobilenet = layer
        break
if mobilenet is None:
    # Might be nested inside a Sequential wrapper
    for layer in model.layers:
        if "mobilenet" in layer.name.lower():
            mobilenet = layer
            break

if mobilenet is not None:
    for sub in mobilenet.layers[:-5]:
        sub.trainable = False
    for sub in mobilenet.layers[-5:]:
        sub.trainable = True
    print(f"MobileNet last-5 unfrozen out of {len(mobilenet.layers)}")
else:
    print("WARN: MobileNetV2 submodel not found by name — only heads will train")

# Unfreeze the dense heads we care about
TRAIN_LAYERS = {"shared_dense", "color_hidden", "color", "category"}
for name in TRAIN_LAYERS:
    try:
        layer = model.get_layer(name)
        layer.trainable = True
        print(f"  unfrozen: {name}")
    except ValueError:
        print(f"  (no layer named {name} — skipping)")

trainable_count = sum(np.prod(v.shape) for v in model.trainable_weights)
print(f"Trainable params: {trainable_count:,}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LR),
    loss={
        "category": "categorical_crossentropy",
        "color": "categorical_crossentropy",
        "season": "categorical_crossentropy",
    },
    loss_weights={"category": 1.0, "color": 0.5, "season": 0.3},
    metrics={"category": "accuracy", "color": "accuracy", "season": "accuracy"},
)


# ── Step 6: Baseline eval (v5 on the original test set) ──
print("\n" + "=" * 60)
print("Step 6: Baseline v5 on test set (pre-finetune)")
print("=" * 60)
baseline = model.evaluate(test_ds, verbose=0, return_dict=True)
print(f"v5 test — Cat {baseline['category_accuracy']:.4f}, Col {baseline['color_accuracy']:.4f}, Sea {baseline['season_accuracy']:.4f}")

db_baseline = model.evaluate(db_test_ds, verbose=0, return_dict=True)
print(f"v5 DB-test — Cat {db_baseline['category_accuracy']:.4f}, Col {db_baseline['color_accuracy']:.4f}")


# ── Step 7: Fine-tune ──
print("\n" + "=" * 60)
print(f"Step 7: Fine-tuning (LR={LR}, epochs={EPOCHS})")
print("=" * 60)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_category_accuracy", patience=3, restore_best_weights=True, verbose=1, mode="max",
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=2, verbose=1, min_lr=1e-8,
    ),
]

history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)


# ── Step 8: Post-finetune eval ──
print("\n" + "=" * 60)
print("Step 8: Post-finetune eval")
print("=" * 60)
after = model.evaluate(test_ds, verbose=0, return_dict=True)
print(f"v6 test — Cat {after['category_accuracy']:.4f}, Col {after['color_accuracy']:.4f}, Sea {after['season_accuracy']:.4f}")
after_db = model.evaluate(db_test_ds, verbose=0, return_dict=True)
print(f"v6 DB-test — Cat {after_db['category_accuracy']:.4f}, Col {after_db['color_accuracy']:.4f}")

# Per-class category accuracy (for direct Flats/Heels/Jacket/Hoodie check)
cat_true, cat_pred = [], []
for batch in test_ds:
    images, labels = batch
    preds = model.predict(images, verbose=0)
    cat_true.extend(tf.argmax(labels["category"], axis=1).numpy())
    cat_pred.extend(tf.argmax(preds["category"], axis=1).numpy())
cat_true = np.array(cat_true)
cat_pred = np.array(cat_pred)

print("\nPer-class CATEGORY accuracy (v6 on Kaggle test):")
per_class_v6 = {}
for i, cat in enumerate(CATEGORIES):
    mask = cat_true == i
    if mask.sum() > 0:
        acc = (cat_pred[mask] == i).mean()
        per_class_v6[cat] = float(acc)
        print(f"  {cat:12s}: {acc:.1%} ({mask.sum()} samples)")


# ── Step 9: Save model, results, labels, TFLite ──
print("\n" + "=" * 60)
print("Step 9: Saving outputs")
print("=" * 60)

model_path = SAVE_DIR / f"fashion_{VARIANT}_multitask.keras"
model.save(model_path)
print(f"Saved: {model_path}")

results = {
    "version": VARIANT,
    "description": f"Partial fine-tune on top of v5 with DB samples (SKIP_LABELS={sorted(SKIP_LABELS)})",
    "epochs_trained": len(history.history["category_accuracy"]),
    "train_samples": len(full_train),
    "db_train_samples": int(full_train["is_db"].sum()),
    "v5_test": {k: float(v) for k, v in baseline.items()},
    "v6_test": {k: float(v) for k, v in after.items()},
    "v5_db_test": {k: float(v) for k, v in db_baseline.items()},
    "v6_db_test": {k: float(v) for k, v in after_db.items()},
    "per_class_category_v6": per_class_v6,
    "categories": CATEGORIES,
    "colors": COLORS,
    "seasons": SEASONS,
    "trainable_params": int(trainable_count),
}
results_path = SAVE_DIR / f"training_results_{VARIANT}.json"
results_path.write_text(json.dumps(results, indent=2))
print(f"Results: {results_path}")

# ── TFLite conversion ──
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]
tflite_bytes = converter.convert()
tflite_path = TFLITE_DIR / f"fashion_multitask_{VARIANT}.tflite"
tflite_path.write_bytes(tflite_bytes)
tflite_size = len(tflite_bytes) / (1024 * 1024)
print(f"TFLite: {tflite_path} ({tflite_size:.1f} MB)")

# NOTE: we do NOT deploy to app/assets here. After this run, compare v5 vs v6b
# per-class numbers — if v6b is clearly better across the board, run:
#   cp model/tflite/fashion_multitask_v6b.tflite app/assets/fashion_multitask.tflite

print("\n" + "=" * 60)
print(f"{VARIANT.upper()} TRAINING COMPLETE")
print("=" * 60)
print(f"v5 → {VARIANT}  Cat: {baseline['category_accuracy']:.3f} → {after['category_accuracy']:.3f}  "
      f"Col: {baseline['color_accuracy']:.3f} → {after['color_accuracy']:.3f}  "
      f"Sea: {baseline['season_accuracy']:.3f} → {after['season_accuracy']:.3f}")
for cat in ["Flats", "Heels", "Jacket", "Hoodie", "Coat", "Sweater"]:
    if cat in per_class_v6:
        print(f"  {cat:8s}: {per_class_v6[cat]:.1%}")
