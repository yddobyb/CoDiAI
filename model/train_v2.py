"""Fashion Codi AI - Improved Model Training Script (v2)
MobileNetV2 Transfer Learning with enhanced augmentation for better real-world generalization.

Improvements over v1:
- Enhanced data augmentation (saturation, hue, noise, rotation)
- Label smoothing (0.1) to reduce overconfidence
- More layers unfrozen in fine-tuning (50 vs 30)
- Longer Phase 2 training (25 epochs, patience 6)
- No MAX_PER_CLASS cap — use all available training data
"""
import tensorflow as tf
import pandas as pd
import numpy as np
import json
import os

IMG_SIZE = 224
BATCH_SIZE = 32
DATA_DIR = '/Users/parkyoungbin/Desktop/ml2/model/data'
SAVE_DIR = '/Users/parkyoungbin/Desktop/ml2/model/saved_model'
TFLITE_DIR = '/Users/parkyoungbin/Desktop/ml2/model/tflite'
FLUTTER_ASSETS = '/Users/parkyoungbin/Desktop/ml2/app/assets'
LABEL_SMOOTHING = 0.1

# ===== 데이터 로드 (전체 사용, cap 제거) =====
train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
val_df = pd.read_csv(os.path.join(DATA_DIR, 'val.csv'))

labels_sorted = sorted(train_df['label'].unique())
label2idx = {l: i for i, l in enumerate(labels_sorted)}
NUM_CLASSES = len(labels_sorted)

train_df['label_idx'] = train_df['label'].map(label2idx)
val_df['label_idx'] = val_df['label'].map(label2idx)

print(f'Classes: {labels_sorted}')
print(f'Train: {len(train_df)} | Val: {len(val_df)}')
print(f'\nTrain distribution:')
print(train_df['label'].value_counts().to_string())

# Class weights
from sklearn.utils.class_weight import compute_class_weight
cw_arr = compute_class_weight('balanced', classes=np.arange(NUM_CLASSES), y=train_df['label_idx'].values)
class_weights = {i: w for i, w in enumerate(cw_arr)}
print(f'\nClass weights: {class_weights}')

# ===== tf.data Pipeline =====
def load_and_preprocess(image_path, label):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label

def augment(image, label):
    # Basic spatial augmentation
    image = tf.image.random_flip_left_right(image)

    # Random rotation (up to ±15 degrees)
    angle = tf.random.uniform([], -0.26, 0.26)  # radians (~15 degrees)
    image = rotate_image(image, angle)

    # Random crop (zoom effect)
    image = tf.image.resize(image, [IMG_SIZE + 30, IMG_SIZE + 30])
    image = tf.image.random_crop(image, [IMG_SIZE, IMG_SIZE, 3])

    # Color augmentation (stronger than v1)
    image = tf.image.random_brightness(image, 0.2)
    image = tf.image.random_contrast(image, 0.7, 1.3)
    image = tf.image.random_saturation(image, 0.7, 1.3)
    image = tf.image.random_hue(image, 0.05)

    # Random Gaussian noise
    if tf.random.uniform([]) > 0.5:
        noise = tf.random.normal(shape=tf.shape(image), mean=0.0, stddev=0.03)
        image = image + noise

    # Clip to valid range for MobileNetV2 preprocessing ([-1, 1])
    image = tf.clip_by_value(image, -1.0, 1.0)

    return image, label

def rotate_image(image, angle):
    """Rotate image by angle (radians) with reflection padding."""
    cos_a = tf.cos(angle)
    sin_a = tf.sin(angle)
    # Rotation matrix as flat [8] for tfa-free rotation
    transform = [cos_a, -sin_a, 0.0,
                 sin_a, cos_a, 0.0,
                 0.0, 0.0]
    image_shape = tf.shape(image)
    h = tf.cast(image_shape[0], tf.float32)
    w = tf.cast(image_shape[1], tf.float32)
    # Center the rotation
    cx = w / 2.0
    cy = h / 2.0
    tx = cx - cos_a * cx + sin_a * cy
    ty = cy - sin_a * cx - cos_a * cy
    transform = [cos_a, -sin_a, tx,
                 sin_a, cos_a, ty,
                 0.0, 0.0]
    image = tf.expand_dims(image, 0)
    image = tf.raw_ops.ImageProjectiveTransformV3(
        images=image,
        transforms=[transform],
        output_shape=[IMG_SIZE, IMG_SIZE],
        interpolation='BILINEAR',
        fill_mode='REFLECT',
        fill_value=0.0,
    )
    image = tf.squeeze(image, 0)
    return image

def make_dataset(dataframe, training=False):
    paths = dataframe['image_path'].values
    labels = tf.one_hot(dataframe['label_idx'].values, NUM_CLASSES)
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.shuffle(4096)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(train_df, training=True)
val_ds = make_dataset(val_df, training=False)

# ===== Phase 1: Backbone Frozen =====
print('\n===== Phase 1: Backbone Frozen =====')
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
    metrics=['accuracy']
)

callbacks_p1 = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True),
]

history_p1 = model.fit(
    train_ds, validation_data=val_ds,
    epochs=15, class_weight=class_weights,
    callbacks=callbacks_p1
)
p1_best = max(history_p1.history['val_accuracy'])
print(f'\nPhase 1 Best val_accuracy: {p1_best:.4f}')

# ===== Phase 2: Fine-tuning (unfreeze last 50 layers) =====
print('\n===== Phase 2: Fine-tuning (50 layers) =====')
base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

trainable_count = sum(1 for l in base_model.layers if l.trainable)
print(f'Trainable backbone layers: {trainable_count}/{len(base_model.layers)}')

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING),
    metrics=['accuracy']
)

callbacks_p2 = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1),
]

history_p2 = model.fit(
    train_ds, validation_data=val_ds,
    epochs=25, class_weight=class_weights,
    callbacks=callbacks_p2
)
p2_best = max(history_p2.history['val_accuracy'])
print(f'\nPhase 2 Best val_accuracy: {p2_best:.4f}')

# ===== 저장 =====
model_path = os.path.join(SAVE_DIR, 'fashion_final_v2.keras')
model.save(model_path)

results = {
    'version': 'v2',
    'improvements': [
        'Enhanced augmentation (rotation, saturation, hue, noise)',
        'Label smoothing 0.1',
        'Dense(256) instead of Dense(128)',
        'Unfreeze last 50 layers (was 30)',
        'No MAX_PER_CLASS cap (full dataset)',
    ],
    'phase1_best_val_acc': float(p1_best),
    'phase2_best_val_acc': float(p2_best),
    'phase1_epochs': len(history_p1.history['accuracy']),
    'phase2_epochs': len(history_p2.history['accuracy']),
    'final_val_acc': float(history_p2.history['val_accuracy'][-1]),
    'classes': labels_sorted,
    'num_classes': NUM_CLASSES,
    'train_samples': len(train_df),
}

with open(os.path.join(SAVE_DIR, 'training_results_v2.json'), 'w') as f:
    json.dump(results, f, indent=2)

# labels.txt 저장
with open(os.path.join(DATA_DIR, 'labels.txt'), 'w') as f:
    for l in labels_sorted:
        f.write(l + '\n')

# ===== TFLite 변환 =====
print('\n===== TFLite Conversion =====')
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]
tflite_model = converter.convert()

tflite_path = os.path.join(TFLITE_DIR, 'fashion_category.tflite')
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)

tflite_size_mb = len(tflite_model) / (1024 * 1024)
print(f'TFLite model saved: {tflite_path} ({tflite_size_mb:.1f} MB)')

# Flutter assets에 복사
import shutil
shutil.copy2(tflite_path, os.path.join(FLUTTER_ASSETS, 'fashion_category.tflite'))
shutil.copy2(os.path.join(DATA_DIR, 'labels.txt'), os.path.join(FLUTTER_ASSETS, 'labels_category.txt'))
print(f'Copied to Flutter assets: {FLUTTER_ASSETS}')

# ===== 완료 =====
print('\n===== DONE =====')
print(f'Phase 1 best: {p1_best:.4f}')
print(f'Phase 2 best: {p2_best:.4f}')
print(f'Model saved: {model_path}')
print(f'TFLite saved: {tflite_path} ({tflite_size_mb:.1f} MB)')
print(f'Flutter assets updated.')
