"""Fashion Codi AI - Model Training Script
MobileNetV2 Transfer Learning: Phase 1 (frozen) + Phase 2 (fine-tune)
"""
import tensorflow as tf
import pandas as pd
import numpy as np
import json
import os

IMG_SIZE = 224
BATCH_SIZE = 32
MAX_PER_CLASS = 1200  # CPU 학습 시간 관리를 위해 cap
DATA_DIR = '/Users/parkyoungbin/Desktop/ml2/model/data'
SAVE_DIR = '/Users/parkyoungbin/Desktop/ml2/model/saved_model'

# ===== 데이터 로드 + 서브샘플링 =====
train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
val_df = pd.read_csv(os.path.join(DATA_DIR, 'val.csv'))

labels_sorted = sorted(train_df['label'].unique())
label2idx = {l: i for i, l in enumerate(labels_sorted)}
NUM_CLASSES = len(labels_sorted)

train_df['label_idx'] = train_df['label'].map(label2idx)
val_df['label_idx'] = val_df['label'].map(label2idx)

# 클래스당 MAX_PER_CLASS로 cap
sampled = []
for label in labels_sorted:
    subset = train_df[train_df['label'] == label]
    if len(subset) > MAX_PER_CLASS:
        subset = subset.sample(n=MAX_PER_CLASS, random_state=42)
    sampled.append(subset)
train_df = pd.concat(sampled, ignore_index=True)

print(f'Classes: {labels_sorted}')
print(f'Train: {len(train_df)} | Val: {len(val_df)}')
print(f'\nTrain distribution:')
print(train_df['label'].value_counts().to_string())

# Class weights
from sklearn.utils.class_weight import compute_class_weight
cw_arr = compute_class_weight('balanced', classes=np.arange(NUM_CLASSES), y=train_df['label_idx'].values)
class_weights = {i: w for i, w in enumerate(cw_arr)}

# ===== tf.data Pipeline =====
def load_and_preprocess(image_path, label):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label

def augment(image, label):
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
        ds = ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.shuffle(2048)
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
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_p1 = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True),
]

history_p1 = model.fit(
    train_ds, validation_data=val_ds,
    epochs=10, class_weight=class_weights,
    callbacks=callbacks_p1
)
p1_best = max(history_p1.history['val_accuracy'])
print(f'\nPhase 1 Best val_accuracy: {p1_best:.4f}')

# ===== Phase 2: Fine-tuning =====
print('\n===== Phase 2: Fine-tuning =====')
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_p2 = [
    tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=4, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1)
]

history_p2 = model.fit(
    train_ds, validation_data=val_ds,
    epochs=15, class_weight=class_weights,
    callbacks=callbacks_p2
)
p2_best = max(history_p2.history['val_accuracy'])
print(f'\nPhase 2 Best val_accuracy: {p2_best:.4f}')

# ===== 저장 =====
model.save(os.path.join(SAVE_DIR, 'fashion_final.keras'))

results = {
    'phase1_best_val_acc': float(p1_best),
    'phase2_best_val_acc': float(p2_best),
    'phase1_epochs': len(history_p1.history['accuracy']),
    'phase2_epochs': len(history_p2.history['accuracy']),
    'final_val_acc': float(history_p2.history['val_accuracy'][-1]),
    'classes': labels_sorted,
    'num_classes': NUM_CLASSES,
    'train_samples': len(train_df),
}

with open(os.path.join(SAVE_DIR, 'training_results.json'), 'w') as f:
    json.dump(results, f, indent=2)

# labels.txt 저장
with open(os.path.join(DATA_DIR, 'labels.txt'), 'w') as f:
    for l in labels_sorted:
        f.write(l + '\n')

print('\n===== DONE =====')
print(f'Phase 1 best: {p1_best:.4f}')
print(f'Phase 2 best: {p2_best:.4f}')
print(f'Model saved: {SAVE_DIR}/fashion_final.keras')
print(f'Labels saved: {DATA_DIR}/labels.txt')
