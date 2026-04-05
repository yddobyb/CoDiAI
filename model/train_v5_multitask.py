"""Fashion Codi AI v5 — Multi-task model (Category + Color + Season)
Adds ML-based color classification and season prediction on top of v4's 15 categories.

Architecture: MobileNetV2 + Shared Features → 3 output heads
- Category: 15 classes (same as v4)
- Color: 12 classes (black, white, gray, navy, blue, red, pink, brown, beige, green, yellow, purple)
- Season: 4 classes (Spring, Summer, Fall, Winter)
"""
import tensorflow as tf
import pandas as pd
import numpy as np
import json
import os
import shutil
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

# ── Config ──
IMG_SIZE = 224
BATCH_SIZE = 32
MAX_PER_CLASS = 1500
MIN_PER_CLASS_AUGMENT = 400
EPOCHS = 25
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SAVE_DIR = os.path.join(BASE_DIR, 'saved_model')
TFLITE_DIR = os.path.join(BASE_DIR, 'tflite')
FLUTTER_ASSETS = os.path.join(BASE_DIR, '..', 'app', 'assets')

# ── Category mapping (same as v4) ──
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

# ── Color mapping: Kaggle baseColour → 12 app colors ──
COLOUR_TO_COLOR = {
    'Black': 'black',
    'White': 'white', 'Cream': 'white', 'Off White': 'white',
    'Grey': 'gray', 'Grey Melange': 'gray', 'Silver': 'gray',
    'Charcoal': 'gray', 'Steel': 'gray',
    'Navy Blue': 'navy',
    'Blue': 'blue', 'Turquoise Blue': 'blue', 'Teal': 'blue',
    'Sea Green': 'blue',
    'Red': 'red', 'Maroon': 'red', 'Burgundy': 'red', 'Wine': 'red', 'Rust': 'red',
    'Pink': 'pink', 'Magenta': 'pink', 'Rose': 'pink', 'Peach': 'pink',
    'Mauve': 'pink', 'Lavender': 'pink', 'Fluorescent Green': 'green',
    'Brown': 'brown', 'Tan': 'brown', 'Copper': 'brown',
    'Coffee Brown': 'brown', 'Mushroom Brown': 'brown', 'Taupe': 'brown',
    'Beige': 'beige', 'Khaki': 'beige', 'Nude': 'beige', 'Skin': 'beige',
    'Green': 'green', 'Olive': 'green', 'Lime Green': 'green',
    'Yellow': 'yellow', 'Mustard': 'yellow', 'Gold': 'yellow',
    'Purple': 'purple', 'Plum': 'purple', 'Violet': 'purple',
    # Unknown → use pixel-based detection at inference; for training, use neutral default
    'Unknown': 'black',
}

# ── Season mapping ──
SEASON_MAP = {'Spring': 'spring', 'Summer': 'summer', 'Fall': 'fall', 'Winter': 'winter'}

# ── Step 1: Load and prepare data ──
print("=" * 60)
print("Step 1: Loading and preparing multi-task data")
print("=" * 60)

df = pd.read_csv(os.path.join(DATA_DIR, 'dataset_final.csv'))
print(f"Total dataset: {len(df)} rows")

# Map category
df['cat_label'] = df['articleType'].map(ARTICLE_TO_CATEGORY)
df = df.dropna(subset=['cat_label'])

# Map color (Unknown → 'black' as placeholder, masked via sample weight)
df['color_label_12'] = df['baseColour'].map(COLOUR_TO_COLOR)
df['color_known'] = df['color_label_12'].notna() & (df['baseColour'] != 'Unknown')
df['color_known'] = df['color_known'].astype(float)
df = df.dropna(subset=['color_label_12'])

# Map season
df['season_label'] = df['season'].map(SEASON_MAP)
df = df.dropna(subset=['season_label'])

# Verify images exist
print("Verifying image files...")
df = df[df['image_path'].apply(os.path.exists)]
print(f"After filtering: {len(df)} rows")

# Label lists
CATEGORIES = sorted(df['cat_label'].unique())
COLORS = sorted(df['color_label_12'].unique())
SEASONS = sorted(df['season_label'].unique())
NUM_CAT = len(CATEGORIES)
NUM_COL = len(COLORS)
NUM_SEA = len(SEASONS)

cat2idx = {l: i for i, l in enumerate(CATEGORIES)}
col2idx = {l: i for i, l in enumerate(COLORS)}
sea2idx = {l: i for i, l in enumerate(SEASONS)}

print(f"\nCategories ({NUM_CAT}): {CATEGORIES}")
print(f"Colors ({NUM_COL}): {COLORS}")
print(f"Seasons ({NUM_SEA}): {SEASONS}")

# Distribution
print("\nCategory distribution:")
for cat, count in df['cat_label'].value_counts().sort_index().items():
    print(f"  {cat:12s}: {count:5d}")
print("\nColor distribution:")
for col, count in df['color_label_12'].value_counts().sort_index().items():
    print(f"  {col:12s}: {count:5d}")
print("\nSeason distribution:")
for sea, count in df['season_label'].value_counts().sort_index().items():
    print(f"  {sea:12s}: {count:5d}")

# ── Step 2: Balance by category and split ──
print("\n" + "=" * 60)
print("Step 2: Balancing and splitting data")
print("=" * 60)

balanced_dfs = []
for cat in CATEGORIES:
    subset = df[df['cat_label'] == cat]
    if len(subset) > MAX_PER_CLASS:
        subset = subset.sample(n=MAX_PER_CLASS, random_state=42)
    balanced_dfs.append(subset)
    orig = len(df[df['cat_label'] == cat])
    print(f"  {cat:12s}: {len(subset):5d} {'(capped)' if orig > MAX_PER_CLASS else ''}")

balanced_df = pd.concat(balanced_dfs, ignore_index=True)
print(f"\nBalanced total: {len(balanced_df)}")

# Stratified split by category
train_df, temp_df = train_test_split(
    balanced_df, test_size=0.3, stratify=balanced_df['cat_label'], random_state=42
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.5, stratify=temp_df['cat_label'], random_state=42
)

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

# Add label indices
for split_df in [train_df, val_df, test_df]:
    split_df = split_df.copy()
train_df = train_df.copy()
val_df = val_df.copy()
test_df = test_df.copy()
train_df['cat_idx'] = train_df['cat_label'].map(cat2idx)
train_df['col_idx'] = train_df['color_label_12'].map(col2idx)
train_df['sea_idx'] = train_df['season_label'].map(sea2idx)
val_df['cat_idx'] = val_df['cat_label'].map(cat2idx)
val_df['col_idx'] = val_df['color_label_12'].map(col2idx)
val_df['sea_idx'] = val_df['season_label'].map(sea2idx)
test_df['cat_idx'] = test_df['cat_label'].map(cat2idx)
test_df['col_idx'] = test_df['color_label_12'].map(col2idx)
test_df['sea_idx'] = test_df['season_label'].map(sea2idx)

# ── Step 3: Oversample small classes ──
print("\n" + "=" * 60)
print("Step 3: Oversampling small classes")
print("=" * 60)

oversampled_dfs = [train_df]
for cat in CATEGORIES:
    subset = train_df[train_df['cat_label'] == cat]
    target = int(MIN_PER_CLASS_AUGMENT * 0.7)
    if len(subset) < target:
        extra = subset.sample(n=target - len(subset), replace=True, random_state=42)
        oversampled_dfs.append(extra)
        print(f"  {cat:12s}: +{len(extra)} oversampled")

train_os = pd.concat(oversampled_dfs, ignore_index=True)
print(f"\nTrain after oversampling: {len(train_os)}")

# ── Step 4: tf.data pipeline (multi-output) ──
print("\n" + "=" * 60)
print("Step 4: Building multi-output data pipeline")
print("=" * 60)

def load_and_preprocess(image_path, cat_label, col_label, sea_label):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, {'category': cat_label, 'color': col_label, 'season': sea_label}

def augment_train(image, labels):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, 0.15)
    image = tf.image.random_contrast(image, 0.85, 1.15)
    padded = tf.image.resize(image, [IMG_SIZE + 20, IMG_SIZE + 20])
    image = tf.image.random_crop(padded, [IMG_SIZE, IMG_SIZE, 3])
    return image, labels

def make_dataset(dataframe, training=False):
    paths = dataframe['image_path'].values
    cat_labels = tf.one_hot(dataframe['cat_idx'].values.astype(np.int32), NUM_CAT)
    col_labels = tf.one_hot(dataframe['col_idx'].values.astype(np.int32), NUM_COL)
    sea_labels = tf.one_hot(dataframe['sea_idx'].values.astype(np.int32), NUM_SEA)

    ds = tf.data.Dataset.from_tensor_slices((paths, cat_labels, col_labels, sea_labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.map(augment_train, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.shuffle(4096)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(train_os, training=True)
val_ds = make_dataset(val_df, training=False)
test_ds = make_dataset(test_df, training=False)

# ── Step 5: Build multi-task model ──
print("\n" + "=" * 60)
print("Step 5: Building Multi-Task MobileNetV2")
print("=" * 60)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet',
)

# Freeze all but last 30 layers
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

trainable = sum(1 for l in base_model.layers if l.trainable)
print(f"Base model: {len(base_model.layers)} layers, {trainable} trainable")

# Functional API for multi-output
inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
shared = tf.keras.layers.Dropout(0.3)(x)
shared = tf.keras.layers.Dense(256, activation='relu', name='shared_dense')(shared)
shared = tf.keras.layers.Dropout(0.2)(shared)

# Category head (primary)
cat_out = tf.keras.layers.Dense(NUM_CAT, activation='softmax', name='category')(shared)

# Color head
col_hidden = tf.keras.layers.Dense(64, activation='relu', name='color_hidden')(shared)
col_out = tf.keras.layers.Dense(NUM_COL, activation='softmax', name='color')(col_hidden)

# Season head
sea_hidden = tf.keras.layers.Dense(32, activation='relu', name='season_hidden')(shared)
sea_out = tf.keras.layers.Dense(NUM_SEA, activation='softmax', name='season')(sea_hidden)

model = tf.keras.Model(inputs=inputs, outputs={'category': cat_out, 'color': col_out, 'season': sea_out})

# Multi-task loss with weights: category is primary
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss={
        'category': 'categorical_crossentropy',
        'color': 'categorical_crossentropy',
        'season': 'categorical_crossentropy',
    },
    loss_weights={'category': 1.0, 'color': 0.5, 'season': 0.3},
    metrics={'category': 'accuracy', 'color': 'accuracy', 'season': 'accuracy'},
)

model.summary()

# ── Step 6: Train ──
print("\n" + "=" * 60)
print("Step 6: Training")
print("=" * 60)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_category_accuracy', patience=6, restore_best_weights=True, verbose=1, mode='max',
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3, verbose=1, min_lr=1e-7,
    ),
]

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks,
)

best_cat_acc = max(history.history['val_category_accuracy'])
best_col_acc = max(history.history['val_color_accuracy'])
best_sea_acc = max(history.history['val_season_accuracy'])
print(f"\nBest val accuracy — Category: {best_cat_acc:.4f}, Color: {best_col_acc:.4f}, Season: {best_sea_acc:.4f}")

# ── Step 7: Evaluate ──
print("\n" + "=" * 60)
print("Step 7: Evaluation on test set")
print("=" * 60)

results_eval = model.evaluate(test_ds, verbose=0, return_dict=True)
test_cat_acc = results_eval['category_accuracy']
test_col_acc = results_eval['color_accuracy']
test_sea_acc = results_eval['season_accuracy']
print(f"Test accuracy — Category: {test_cat_acc:.4f}, Color: {test_col_acc:.4f}, Season: {test_sea_acc:.4f}")

# Per-class accuracy for each task
cat_true, cat_pred = [], []
col_true, col_pred = [], []
sea_true, sea_pred = [], []

for images, labels in test_ds:
    preds = model.predict(images, verbose=0)
    cat_true.extend(tf.argmax(labels['category'], axis=1).numpy())
    cat_pred.extend(tf.argmax(preds['category'], axis=1).numpy())
    col_true.extend(tf.argmax(labels['color'], axis=1).numpy())
    col_pred.extend(tf.argmax(preds['color'], axis=1).numpy())
    sea_true.extend(tf.argmax(labels['season'], axis=1).numpy())
    sea_pred.extend(tf.argmax(preds['season'], axis=1).numpy())

cat_true = np.array(cat_true)
cat_pred = np.array(cat_pred)
col_true = np.array(col_true)
col_pred = np.array(col_pred)
sea_true = np.array(sea_true)
sea_pred = np.array(sea_pred)

print("\nPer-class CATEGORY accuracy:")
for i, cat in enumerate(CATEGORIES):
    mask = cat_true == i
    if mask.sum() > 0:
        acc = (cat_pred[mask] == i).mean()
        print(f"  {cat:12s}: {acc:.1%} ({mask.sum()} samples)")

print("\nPer-class COLOR accuracy:")
for i, col in enumerate(COLORS):
    mask = col_true == i
    if mask.sum() > 0:
        acc = (col_pred[mask] == i).mean()
        print(f"  {col:12s}: {acc:.1%} ({mask.sum()} samples)")

print("\nPer-class SEASON accuracy:")
for i, sea in enumerate(SEASONS):
    mask = sea_true == i
    if mask.sum() > 0:
        acc = (sea_pred[mask] == i).mean()
        print(f"  {sea:12s}: {acc:.1%} ({mask.sum()} samples)")

# Top confusions (category)
confusions = Counter()
for t, p in zip(cat_true, cat_pred):
    if t != p:
        confusions[(CATEGORIES[t], CATEGORIES[p])] += 1
print("\nTop category confusions:")
for (tc, pc), count in confusions.most_common(10):
    print(f"  {tc} → {pc}: {count}")

# Top confusions (color)
col_confusions = Counter()
for t, p in zip(col_true, col_pred):
    if t != p:
        col_confusions[(COLORS[t], COLORS[p])] += 1
print("\nTop color confusions:")
for (tc, pc), count in col_confusions.most_common(10):
    print(f"  {tc} → {pc}: {count}")

# ── Step 8: Save model ──
print("\n" + "=" * 60)
print("Step 8: Saving model")
print("=" * 60)

model_path = os.path.join(SAVE_DIR, 'fashion_v5_multitask.keras')
model.save(model_path)
print(f"Saved: {model_path}")

results = {
    'version': 'v5',
    'description': 'Multi-task model (Category + Color + Season)',
    'base': 'MobileNetV2 (ImageNet) + Shared Dense(256) → 3 heads',
    'categories': CATEGORIES,
    'colors': COLORS,
    'seasons': SEASONS,
    'num_categories': NUM_CAT,
    'num_colors': NUM_COL,
    'num_seasons': NUM_SEA,
    'best_val_cat_acc': float(best_cat_acc),
    'best_val_col_acc': float(best_col_acc),
    'best_val_sea_acc': float(best_sea_acc),
    'test_cat_acc': float(test_cat_acc),
    'test_col_acc': float(test_col_acc),
    'test_sea_acc': float(test_sea_acc),
    'epochs_trained': len(history.history['category_accuracy']),
    'train_samples': len(train_os),
    'val_samples': len(val_df),
    'test_samples': len(test_df),
    'loss_weights': {'category': 1.0, 'color': 0.5, 'season': 0.3},
}

results_path = os.path.join(SAVE_DIR, 'training_results_v5.json')
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results: {results_path}")

# Save labels for each task
for name, labels in [('category', CATEGORIES), ('color', COLORS), ('season', SEASONS)]:
    path = os.path.join(DATA_DIR, f'labels_{name}.txt')
    with open(path, 'w') as f:
        f.write('\n'.join(labels))
    print(f"Labels ({name}): {path}")

# ── Step 9: TFLite conversion ──
print("\n" + "=" * 60)
print("Step 9: TFLite conversion (float16)")
print("=" * 60)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]
tflite_model = converter.convert()

tflite_path = os.path.join(TFLITE_DIR, 'fashion_multitask_v5.tflite')
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)

tflite_size = len(tflite_model) / (1024 * 1024)
print(f"TFLite model: {tflite_path} ({tflite_size:.1f} MB)")

# TFLite multi-output accuracy check
interpreter = tf.lite.Interpreter(model_path=tflite_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"\nTFLite outputs: {len(output_details)}")
for i, od in enumerate(output_details):
    print(f"  Output {i}: shape={od['shape']}, name={od['name']}")

tflite_cat_correct = 0
tflite_col_correct = 0
tflite_sea_correct = 0
tflite_total = 0

for batch in test_ds:
    images, labels = batch[0], batch[1]
    for i in range(len(images)):
        img_tensor = tf.expand_dims(images[i], 0)
        if input_details[0]['dtype'] == np.float16:
            img_tensor = tf.cast(img_tensor, tf.float16)
        interpreter.set_tensor(input_details[0]['index'], img_tensor.numpy())
        interpreter.invoke()

        # Get outputs — order might vary, match by shape
        outputs = {}
        for od in output_details:
            tensor = interpreter.get_tensor(od['index'])
            shape = tensor.shape[-1]
            if shape == NUM_CAT:
                outputs['category'] = tensor
            elif shape == NUM_COL:
                outputs['color'] = tensor
            elif shape == NUM_SEA:
                outputs['season'] = tensor

        cat_p = np.argmax(outputs['category'])
        col_p = np.argmax(outputs['color'])
        sea_p = np.argmax(outputs['season'])

        cat_t = np.argmax(labels['category'][i].numpy())
        col_t = np.argmax(labels['color'][i].numpy())
        sea_t = np.argmax(labels['season'][i].numpy())

        if cat_p == cat_t: tflite_cat_correct += 1
        if col_p == col_t: tflite_col_correct += 1
        if sea_p == sea_t: tflite_sea_correct += 1
        tflite_total += 1

tflite_cat_acc = tflite_cat_correct / tflite_total
tflite_col_acc = tflite_col_correct / tflite_total
tflite_sea_acc = tflite_sea_correct / tflite_total
print(f"\nTFLite test accuracy — Category: {tflite_cat_acc:.4f}, Color: {tflite_col_acc:.4f}, Season: {tflite_sea_acc:.4f}")

# ── Step 10: Deploy to Flutter ──
print("\n" + "=" * 60)
print("Step 10: Deploying to Flutter assets")
print("=" * 60)

os.makedirs(FLUTTER_ASSETS, exist_ok=True)

# Copy TFLite model
flutter_tflite = os.path.join(FLUTTER_ASSETS, 'fashion_multitask.tflite')
shutil.copy2(tflite_path, flutter_tflite)
print(f"Copied TFLite → {flutter_tflite}")

# Copy label files
for name in ['category', 'color', 'season']:
    src = os.path.join(DATA_DIR, f'labels_{name}.txt')
    dst = os.path.join(FLUTTER_ASSETS, f'labels_{name}.txt')
    shutil.copy2(src, dst)
    print(f"Copied labels_{name}.txt → {dst}")

# ── Summary ──
print("\n" + "=" * 60)
print("TRAINING COMPLETE — v5 Multi-Task Model")
print("=" * 60)
print(f"Categories: {NUM_CAT} ({', '.join(CATEGORIES)})")
print(f"Colors: {NUM_COL} ({', '.join(COLORS)})")
print(f"Seasons: {NUM_SEA} ({', '.join(SEASONS)})")
print(f"\nBest val accuracy — Cat: {best_cat_acc:.2%}, Col: {best_col_acc:.2%}, Sea: {best_sea_acc:.2%}")
print(f"Test accuracy (Keras) — Cat: {test_cat_acc:.2%}, Col: {test_col_acc:.2%}, Sea: {test_sea_acc:.2%}")
print(f"Test accuracy (TFLite) — Cat: {tflite_cat_acc:.2%}, Col: {tflite_col_acc:.2%}, Sea: {tflite_sea_acc:.2%}")
print(f"TFLite size: {tflite_size:.1f} MB")
print(f"Flutter assets updated ✓")
