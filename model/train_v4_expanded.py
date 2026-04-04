"""Fashion Codi AI v4 — Expanded 15-category model
Expands from 9 → 15 categories using existing Kaggle dataset.

New categories: Sweater, Skirt, Shorts, Coat, Flats, Heels
Architecture: MobileNetV2 + Custom Head (GAP → Dense(256) → Dense(15))
"""
import tensorflow as tf
import pandas as pd
import numpy as np
import json
import os
import shutil
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

# ── Config ──
IMG_SIZE = 224
BATCH_SIZE = 32
MAX_PER_CLASS = 1500
MIN_PER_CLASS_AUGMENT = 400  # Target min after augmentation
EPOCHS = 25
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SAVE_DIR = os.path.join(BASE_DIR, 'saved_model')
TFLITE_DIR = os.path.join(BASE_DIR, 'tflite')
FLUTTER_ASSETS = os.path.join(BASE_DIR, '..', 'app', 'assets')

# ── Step 1: Remap articleTypes to 15 categories ──
print("=" * 60)
print("Step 1: Remapping to 15 categories")
print("=" * 60)

ARTICLE_TO_CATEGORY = {
    # Tops
    'Tshirts': 'T-shirt',
    'Tops': 'T-shirt',
    'Shirts': 'Shirt',
    'Hoodie': 'Hoodie',
    'Sweatshirts': 'Sweater',
    'Sweaters': 'Sweater',
    # Outerwear
    'Jackets': 'Jacket',
    'Blazer': 'Jacket',
    'Blazers': 'Jacket',
    'Outwear': 'Coat',
    # Bottoms
    'Jeans': 'Jeans',
    'Trousers': 'Pants',
    'Track Pants': 'Pants',
    'Shorts': 'Shorts',
    'Skirt': 'Skirt',
    'Skirts': 'Skirt',
    'Dress': 'Dress',
    'Dresses': 'Dress',
    'Jumpsuit': 'Dress',
    # Shoes
    'Sports Shoes': 'Sneakers',
    'Casual Shoes': 'Sneakers',
    'Formal Shoes': 'Boots',
    'Flats': 'Flats',
    'Heels': 'Heels',
}

df = pd.read_csv(os.path.join(DATA_DIR, 'dataset_final.csv'))
print(f"Total dataset: {len(df)} rows")

# Remap
df['new_label'] = df['articleType'].map(ARTICLE_TO_CATEGORY)
df = df.dropna(subset=['new_label'])

# Verify images exist
print("Verifying image files...")
df = df[df['image_path'].apply(os.path.exists)]
print(f"After verification: {len(df)} rows")

# Print distribution
print("\nCategory distribution:")
dist = df['new_label'].value_counts().sort_index()
for cat, count in dist.items():
    marker = " ← NEW" if cat in ['Sweater', 'Skirt', 'Shorts', 'Coat', 'Flats', 'Heels'] else ""
    print(f"  {cat:12s}: {count:5d}{marker}")

CATEGORIES = sorted(df['new_label'].unique())
NUM_CLASSES = len(CATEGORIES)
label2idx = {l: i for i, l in enumerate(CATEGORIES)}
print(f"\nTotal categories: {NUM_CLASSES}")

# ── Step 2: Balance and split ──
print("\n" + "=" * 60)
print("Step 2: Balancing and splitting data")
print("=" * 60)

# Cap large classes, keep small classes as-is
balanced_dfs = []
for cat in CATEGORIES:
    subset = df[df['new_label'] == cat]
    if len(subset) > MAX_PER_CLASS:
        subset = subset.sample(n=MAX_PER_CLASS, random_state=42)
    balanced_dfs.append(subset)
    print(f"  {cat:12s}: {len(subset):5d} {'(capped)' if len(df[df['new_label'] == cat]) > MAX_PER_CLASS else ''}")

balanced_df = pd.concat(balanced_dfs, ignore_index=True)
print(f"\nBalanced total: {len(balanced_df)}")

# Stratified split: 70% train, 15% val, 15% test
train_df, temp_df = train_test_split(
    balanced_df, test_size=0.3, stratify=balanced_df['new_label'], random_state=42
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.5, stratify=temp_df['new_label'], random_state=42
)

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

# Add label indices
train_df = train_df.copy()
val_df = val_df.copy()
test_df = test_df.copy()
train_df['label_idx'] = train_df['new_label'].map(label2idx)
val_df['label_idx'] = val_df['new_label'].map(label2idx)
test_df['label_idx'] = test_df['new_label'].map(label2idx)

# Print train distribution
print("\nTrain distribution:")
for cat in CATEGORIES:
    count = len(train_df[train_df['new_label'] == cat])
    print(f"  {cat:12s}: {count:5d}")

# ── Step 3: Oversample small classes in training ──
print("\n" + "=" * 60)
print("Step 3: Oversampling small classes")
print("=" * 60)

oversampled_dfs = [train_df]
for cat in CATEGORIES:
    subset = train_df[train_df['new_label'] == cat]
    target = int(MIN_PER_CLASS_AUGMENT * 0.7)  # 70% of target (augmentation handles rest)
    if len(subset) < target:
        extra = subset.sample(n=target - len(subset), replace=True, random_state=42)
        oversampled_dfs.append(extra)
        print(f"  {cat:12s}: +{len(extra)} oversampled (total → {len(subset) + len(extra)})")

train_oversampled = pd.concat(oversampled_dfs, ignore_index=True)
print(f"\nTrain after oversampling: {len(train_oversampled)}")

# Class weights
cw_arr = compute_class_weight(
    'balanced',
    classes=np.arange(NUM_CLASSES),
    y=train_oversampled['label_idx'].values,
)
class_weights = {i: float(w) for i, w in enumerate(cw_arr)}
print("\nClass weights:")
for i, cat in enumerate(CATEGORIES):
    print(f"  {cat:12s}: {class_weights[i]:.3f}")

# ── Step 4: tf.data pipeline ──
print("\n" + "=" * 60)
print("Step 4: Building data pipeline")
print("=" * 60)

def load_and_preprocess(image_path, label):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label

def augment_train(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, 0.2)
    image = tf.image.random_contrast(image, 0.8, 1.2)
    image = tf.image.random_saturation(image, 0.8, 1.2)
    # Random crop
    padded = tf.image.resize(image, [IMG_SIZE + 24, IMG_SIZE + 24])
    image = tf.image.random_crop(padded, [IMG_SIZE, IMG_SIZE, 3])
    return image, label

def make_dataset(dataframe, training=False):
    paths = dataframe['image_path'].values
    labels = tf.one_hot(dataframe['label_idx'].values.astype(np.int32), NUM_CLASSES)
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.map(augment_train, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.shuffle(4096)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(train_oversampled, training=True)
val_ds = make_dataset(val_df, training=False)
test_ds = make_dataset(test_df, training=False)

# ── Step 5: Build model ──
print("\n" + "=" * 60)
print("Step 5: Building MobileNetV2 + Custom Head")
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

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax'),
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

model.summary()

# ── Step 6: Train ──
print("\n" + "=" * 60)
print("Step 6: Training")
print("=" * 60)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=6, restore_best_weights=True, verbose=1,
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3, verbose=1, min_lr=1e-7,
    ),
]

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=callbacks,
)

best_val_acc = max(history.history['val_accuracy'])
final_val_acc = history.history['val_accuracy'][-1]
print(f"\nBest val_accuracy: {best_val_acc:.4f}")
print(f"Final val_accuracy: {final_val_acc:.4f}")

# ── Step 7: Evaluate ──
print("\n" + "=" * 60)
print("Step 7: Evaluation on test set")
print("=" * 60)

test_loss, test_acc = model.evaluate(test_ds, verbose=0)
print(f"Test accuracy (Keras): {test_acc:.4f}")
print(f"Test loss: {test_loss:.4f}")

# Per-class accuracy
y_true = []
y_pred = []
for images, labels in test_ds:
    preds = model.predict(images, verbose=0)
    y_true.extend(tf.argmax(labels, axis=1).numpy())
    y_pred.extend(tf.argmax(preds, axis=1).numpy())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

print("\nPer-class accuracy:")
for i, cat in enumerate(CATEGORIES):
    mask = y_true == i
    if mask.sum() > 0:
        acc = (y_pred[mask] == i).mean()
        total = mask.sum()
        print(f"  {cat:12s}: {acc:.1%} ({total} samples)")

# Confusion pairs (most confused)
from collections import Counter
confusions = Counter()
for t, p in zip(y_true, y_pred):
    if t != p:
        confusions[(CATEGORIES[t], CATEGORIES[p])] += 1

print("\nTop confusions:")
for (true_cat, pred_cat), count in confusions.most_common(10):
    print(f"  {true_cat} → {pred_cat}: {count}")

# ── Step 8: Save model ──
print("\n" + "=" * 60)
print("Step 8: Saving model")
print("=" * 60)

model_path = os.path.join(SAVE_DIR, 'fashion_v4_15cat.keras')
model.save(model_path)
print(f"Saved: {model_path}")

# Save training results
results = {
    'version': 'v4',
    'description': '15-category expanded model',
    'base': 'MobileNetV2 (ImageNet) + Custom Head (GAP → D256 → D15)',
    'categories': CATEGORIES,
    'num_classes': NUM_CLASSES,
    'best_val_acc': float(best_val_acc),
    'final_val_acc': float(final_val_acc),
    'test_acc': float(test_acc),
    'epochs_trained': len(history.history['accuracy']),
    'train_samples': len(train_oversampled),
    'val_samples': len(val_df),
    'test_samples': len(test_df),
    'new_categories': ['Sweater', 'Skirt', 'Shorts', 'Coat', 'Flats', 'Heels'],
}

results_path = os.path.join(SAVE_DIR, 'training_results_v4.json')
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results: {results_path}")

# Save updated labels
labels_path = os.path.join(DATA_DIR, 'labels_v4.txt')
with open(labels_path, 'w') as f:
    f.write('\n'.join(CATEGORIES))
print(f"Labels: {labels_path}")

# ── Step 9: TFLite conversion ──
print("\n" + "=" * 60)
print("Step 9: TFLite conversion (float16)")
print("=" * 60)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]
tflite_model = converter.convert()

tflite_path = os.path.join(TFLITE_DIR, 'fashion_category_v4.tflite')
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)

tflite_size = len(tflite_model) / (1024 * 1024)
print(f"TFLite model: {tflite_path} ({tflite_size:.1f} MB)")

# TFLite accuracy check
interpreter = tf.lite.Interpreter(model_path=tflite_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

tflite_correct = 0
tflite_total = 0
for images, labels in test_ds:
    for i in range(len(images)):
        img = tf.expand_dims(images[i], 0)
        if input_details[0]['dtype'] == np.float16:
            img = tf.cast(img, tf.float16)
        interpreter.set_tensor(input_details[0]['index'], img.numpy())
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
        pred = np.argmax(output)
        true_label = np.argmax(labels[i].numpy())
        if pred == true_label:
            tflite_correct += 1
        tflite_total += 1

tflite_acc = tflite_correct / tflite_total
print(f"TFLite test accuracy: {tflite_acc:.4f}")
print(f"Keras vs TFLite diff: {abs(test_acc - tflite_acc):.4f}")

# ── Step 10: Deploy to Flutter ──
print("\n" + "=" * 60)
print("Step 10: Deploying to Flutter assets")
print("=" * 60)

os.makedirs(FLUTTER_ASSETS, exist_ok=True)

# Copy TFLite model
flutter_tflite = os.path.join(FLUTTER_ASSETS, 'fashion_category.tflite')
shutil.copy2(tflite_path, flutter_tflite)
print(f"Copied TFLite → {flutter_tflite}")

# Copy labels
flutter_labels = os.path.join(FLUTTER_ASSETS, 'labels_category.txt')
shutil.copy2(labels_path, flutter_labels)
print(f"Copied labels → {flutter_labels}")

# Also update main labels.txt
main_labels = os.path.join(DATA_DIR, 'labels.txt')
shutil.copy2(labels_path, main_labels)

# ── Summary ──
print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
print(f"Categories: {NUM_CLASSES} ({', '.join(CATEGORIES)})")
print(f"Best val accuracy: {best_val_acc:.2%}")
print(f"Test accuracy (Keras): {test_acc:.2%}")
print(f"Test accuracy (TFLite): {tflite_acc:.2%}")
print(f"TFLite size: {tflite_size:.1f} MB")
print(f"Flutter assets updated ✓")
print(f"\nNext: Update Flutter app code for new categories")
