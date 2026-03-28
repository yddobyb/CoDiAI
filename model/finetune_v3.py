"""Fashion Codi AI - Fine-tune v1 with real-world shirt photos (v3)
Uses user-collected Google Images shirt photos + synthetic augmentation
to improve Shirt vs Jacket classification on real-world photos.
"""
import tensorflow as tf
import pandas as pd
import numpy as np
import json
import os
import shutil
import glob

IMG_SIZE = 224
BATCH_SIZE = 32
DATA_DIR = '/Users/parkyoungbin/Desktop/ml2/model/data'
SAVE_DIR = '/Users/parkyoungbin/Desktop/ml2/model/saved_model'
TFLITE_DIR = '/Users/parkyoungbin/Desktop/ml2/model/tflite'
FLUTTER_ASSETS = '/Users/parkyoungbin/Desktop/ml2/app/assets'
REALWORLD_SHIRTS = '/Users/parkyoungbin/Desktop/ml2/shirts - Google Search'

# ===== Step 1: Filter usable real-world shirt images =====
print("===== Step 1: Filtering real-world shirt images =====")

valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
min_file_size = 5 * 1024  # 5KB minimum (skip icons/UI elements)

realworld_paths = []
skipped = 0
for f in os.listdir(REALWORLD_SHIRTS):
    fpath = os.path.join(REALWORLD_SHIRTS, f)
    ext = os.path.splitext(f)[1].lower()
    if ext not in valid_extensions:
        skipped += 1
        continue
    if os.path.getsize(fpath) < min_file_size:
        skipped += 1
        continue
    realworld_paths.append(fpath)

print(f"  Usable shirt images: {len(realworld_paths)}")
print(f"  Skipped (icons/SVG/small): {skipped}")

# Validate images can be decoded
valid_paths = []
for p in realworld_paths:
    try:
        raw = tf.io.read_file(p)
        img = tf.image.decode_image(raw, channels=3)
        if img.shape[0] >= 32 and img.shape[1] >= 32:  # minimum size
            valid_paths.append(p)
    except:
        pass

print(f"  Valid (decodable, >=32px): {len(valid_paths)}")

# ===== Step 2: Load original training data =====
print("\n===== Step 2: Loading training data =====")
train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
val_df = pd.read_csv(os.path.join(DATA_DIR, 'val.csv'))

labels_sorted = sorted(train_df['label'].unique())
label2idx = {l: i for i, l in enumerate(labels_sorted)}
NUM_CLASSES = len(labels_sorted)

train_df['label_idx'] = train_df['label'].map(label2idx)
val_df['label_idx'] = val_df['label'].map(label2idx)

# Cap original data per class
MAX_PER_CLASS = 1200
sampled = []
for label in labels_sorted:
    subset = train_df[train_df['label'] == label]
    if len(subset) > MAX_PER_CLASS:
        subset = subset.sample(n=MAX_PER_CLASS, random_state=42)
    sampled.append(subset)
original_df = pd.concat(sampled, ignore_index=True)

# Add real-world shirt images
shirt_idx = label2idx['Shirt']
realworld_records = []
for p in valid_paths:
    realworld_records.append({
        'image_path': p,
        'label': 'Shirt',
        'label_idx': shirt_idx,
    })
realworld_df = pd.DataFrame(realworld_records)

# Also create augmented versions of existing Jacket images
# to balance the additional Shirt data
print("\n===== Step 3: Augmenting Jacket images for balance =====")
AUGMENT_DIR = os.path.join(DATA_DIR, 'realworld', 'Jacket')
os.makedirs(AUGMENT_DIR, exist_ok=True)

jacket_df = train_df[train_df['label'] == 'Jacket']
jacket_aug_records = []
jacket_count = 0

for _, row in jacket_df.iterrows():
    for aug_i in range(2):  # 2 augmented versions per jacket image
        try:
            img = tf.io.read_file(row['image_path'])
            img = tf.image.decode_jpeg(img, channels=3)
            img = tf.cast(img, tf.float32)

            h, w = tf.shape(img)[0], tf.shape(img)[1]
            crop_frac = tf.random.uniform([], 0.65, 0.95)
            crop_h = tf.cast(tf.cast(h, tf.float32) * crop_frac, tf.int32)
            crop_w = tf.cast(tf.cast(w, tf.float32) * crop_frac, tf.int32)
            crop_h = tf.maximum(crop_h, 32)
            crop_w = tf.maximum(crop_w, 32)
            img = tf.image.random_crop(img, [crop_h, crop_w, 3])
            img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])

            img = tf.image.random_brightness(img, 0.25)
            img = tf.image.random_contrast(img, 0.7, 1.3)
            img = tf.image.random_saturation(img, 0.6, 1.4)

            if tf.random.uniform([]) > 0.5:
                noise = tf.random.normal(shape=tf.shape(img), stddev=5.0)
                img = img + noise

            img = tf.clip_by_value(img, 0, 255)
            img = tf.cast(img, tf.uint8)

            save_path = os.path.join(AUGMENT_DIR, f"aug_{row['id']}_{aug_i}.jpg")
            encoded = tf.io.encode_jpeg(img, quality=85)
            tf.io.write_file(save_path, encoded)

            jacket_aug_records.append({
                'image_path': save_path,
                'label': 'Jacket',
                'label_idx': label2idx['Jacket'],
            })
            jacket_count += 1
        except:
            pass

print(f"  Jacket augmented images: {jacket_count}")
jacket_aug_df = pd.DataFrame(jacket_aug_records)

# Combine all data
combined_df = pd.concat([original_df, realworld_df, jacket_aug_df], ignore_index=True)

print(f"\n===== Combined training data =====")
print(f"  Original: {len(original_df)}")
print(f"  Real-world shirts: {len(realworld_df)}")
print(f"  Augmented jackets: {len(jacket_aug_df)}")
print(f"  Total: {len(combined_df)}")
print(f"\nClass distribution:")
print(combined_df['label'].value_counts().to_string())

# Class weights
from sklearn.utils.class_weight import compute_class_weight
cw_arr = compute_class_weight('balanced', classes=np.arange(NUM_CLASSES),
                               y=combined_df['label_idx'].values)
class_weights = {i: w for i, w in enumerate(cw_arr)}

# ===== tf.data Pipeline =====
def load_and_preprocess(image_path, label):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label

def augment_train(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, 0.15)
    image = tf.image.random_contrast(image, 0.8, 1.2)
    image = tf.image.random_crop(
        tf.image.resize(image, [IMG_SIZE + 20, IMG_SIZE + 20]),
        [IMG_SIZE, IMG_SIZE, 3]
    )
    return image, label

def make_dataset(dataframe, training=False):
    paths = dataframe['image_path'].values
    labels = tf.one_hot(dataframe['label_idx'].values, NUM_CLASSES)
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.map(augment_train, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.shuffle(4096)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(combined_df, training=True)
val_ds = make_dataset(val_df, training=False)

# ===== Step 4: Load v1 model and fine-tune =====
print('\n===== Loading v1 model =====')
model = tf.keras.models.load_model(os.path.join(SAVE_DIR, 'fashion_final.keras'))

# Fine-tune: unfreeze last 30 layers (same as v1)
base_model = model.layers[0]
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

trainable_count = sum(1 for l in base_model.layers if l.trainable)
print(f'Trainable backbone layers: {trainable_count}/{len(base_model.layers)}')

# Very low learning rate to preserve existing accuracy
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=5e-6),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=5, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=2, verbose=1),
]

print('\n===== Fine-tuning with real-world data =====')
history = model.fit(
    train_ds, validation_data=val_ds,
    epochs=15, class_weight=class_weights,
    callbacks=callbacks,
)
best_acc = max(history.history['val_accuracy'])
final_acc = history.history['val_accuracy'][-1]
print(f'\nBest val_accuracy: {best_acc:.4f}')
print(f'Final val_accuracy: {final_acc:.4f}')

# ===== Step 5: Save =====
model_path = os.path.join(SAVE_DIR, 'fashion_final_v3.keras')
model.save(model_path)

results = {
    'version': 'v3',
    'base_model': 'v1 (fashion_final.keras, val_acc 90.32%)',
    'strategy': 'Fine-tune v1 with real-world Google shirt images + balanced Jacket augmentation',
    'best_val_acc': float(best_acc),
    'epochs_trained': len(history.history['accuracy']),
    'final_val_acc': float(final_acc),
    'realworld_shirt_images': len(realworld_df),
    'augmented_jacket_images': len(jacket_aug_df),
    'total_train_samples': len(combined_df),
    'classes': labels_sorted,
}

with open(os.path.join(SAVE_DIR, 'training_results_v3.json'), 'w') as f:
    json.dump(results, f, indent=2)

# ===== Step 6: TFLite conversion =====
print('\n===== TFLite Conversion =====')
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]
tflite_model = converter.convert()

tflite_path = os.path.join(TFLITE_DIR, 'fashion_category.tflite')
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)

tflite_size_mb = len(tflite_model) / (1024 * 1024)

shutil.copy2(tflite_path, os.path.join(FLUTTER_ASSETS, 'fashion_category.tflite'))
shutil.copy2(os.path.join(DATA_DIR, 'labels.txt'),
             os.path.join(FLUTTER_ASSETS, 'labels_category.txt'))

print(f'TFLite model: {tflite_path} ({tflite_size_mb:.1f} MB)')
print(f'Copied to Flutter assets')

print('\n===== DONE =====')
print(f'v1 base: 90.32% → v3: {best_acc:.4f}')
print(f'Real-world shirts added: {len(realworld_df)}')
print(f'Augmented jackets added: {len(jacket_aug_df)}')
print(f'Flutter assets updated — ready to rebuild app')
