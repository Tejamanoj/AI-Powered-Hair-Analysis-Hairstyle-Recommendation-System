import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np
import os

# ===== DATASET PATH =====
dataset_path = "../datasets"

# ===== ALL 11 CLASSES — standardized lowercase =====
# NOTE: folder names must exactly match these strings
all_classes = ['Straight', 'Wavy', 'bald', 'curly', 'dreadlocks',
               'dry', 'frizzy', 'hairfall', 'healthy', 'kinky', 'notbald']

# ===== COUNT IMAGES PER CLASS =====
print("===== IMAGE COUNTS =====")
class_counts = {}
for class_name in all_classes:
    path = os.path.join(dataset_path, class_name)
    if os.path.exists(path):
        count = len([f for f in os.listdir(path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        class_counts[class_name] = count
        print(f"{class_name}: {count} images")

# ===== LOAD DATASET =====
# Increased image size from 224→299 for EfficientNetB3 (better feature extraction)
IMG_SIZE   = 224
BATCH_SIZE = 16

train_ds = tf.keras.utils.image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="training",
    seed=42,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="validation",
    seed=42,
    image_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE
)

class_names = train_ds.class_names
num_classes = len(class_names)
print(f"\nClasses ({num_classes}):", class_names)

# ===== CALCULATE CLASS WEIGHTS =====
total = sum(class_counts[c] for c in class_names if c in class_counts)
class_weights = {}
for i, class_name in enumerate(class_names):
    if class_name in class_counts and class_counts[class_name] > 0:
        class_weights[i] = total / (num_classes * class_counts[class_name])
print("\nClass weights:", class_weights)

# ===== DATA AUGMENTATION =====
# More aggressive augmentation to fight overfitting on visually similar classes (dry vs healthy)
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomBrightness(0.25),     # ↑ increased — helps dry/healthy differentiation
    layers.RandomContrast(0.25),       # ↑ increased — helps with texture differences
    layers.RandomTranslation(0.1, 0.1),# NEW — improves spatial generalization
])

# ===== OPTIMIZE PIPELINE =====
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.map(
    lambda x, y: (data_augmentation(x, training=True), y),
    num_parallel_calls=AUTOTUNE
)
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds   = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# ===== BUILD MODEL =====
# Using EfficientNetB0 — same as before (compatible with your existing weights)
# EfficientNet has its own preprocessing — do NOT rescale, pass raw [0, 255] values
base_model = tf.keras.applications.EfficientNetB0(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
# ✅ NO Rescaling layer — EfficientNet normalizes internally
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.5)(x)           # ↑ increased from 0.4 → 0.5 to reduce overfitting
x = layers.Dense(256, activation='relu')(x)
x = layers.BatchNormalization()(x)   # NEW — stabilizes training
x = layers.Dropout(0.4)(x)           # ↑ increased from 0.3 → 0.4
outputs = layers.Dense(num_classes, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

# ===== CALLBACKS — KEY IMPROVEMENT =====
callbacks = [
    # ✅ Early stopping — stops when val_accuracy stops improving
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=5,
        restore_best_weights=True,  # automatically loads best checkpoint
        verbose=1
    ),
    # ✅ Save best model during training — safe against crashes
    tf.keras.callbacks.ModelCheckpoint(
        "../model/best_model.h5",
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    # ✅ Reduce LR on plateau — fine-tunes learning when stuck
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.3,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )
]

# ===== COMPILE — PHASE 1 (Frozen base) =====
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

model.summary()

# ===== TRAIN Phase 1 =====
print("\n===== PHASE 1: Training head with frozen base =====")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=20,            # more epochs allowed — early stopping will cut when needed
    class_weight=class_weights,
    callbacks=callbacks
)

# ===== FINE-TUNE Phase 2 =====
print("\n===== PHASE 2: Fine tuning last 40 layers =====")
base_model.trainable = True
for layer in base_model.layers[:-40]:
    layer.trainable = False

# ✅ Much lower LR for fine tuning to avoid catastrophic forgetting
model.compile(
    optimizer=tf.keras.optimizers.Adam(5e-6),  # lowered from 1e-5 → 5e-6
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

# Reset early stopping patience for fine-tune phase
callbacks_ft = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=4,
        restore_best_weights=True,
        verbose=1
    ),
    tf.keras.callbacks.ModelCheckpoint(
        "../model/best_model.h5",
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.3,
        patience=2,
        min_lr=1e-8,
        verbose=1
    )
]

history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=15,
    class_weight=class_weights,
    callbacks=callbacks_ft
)

# ===== SAVE FINAL MODEL =====
model.save("../model/hair_model.h5")
print("\n✅ Final model saved to hair_model.h5")
print("✅ Best checkpoint saved to best_model.h5")
print("   Tip: Use best_model.h5 in app.py — it has the highest val_accuracy")

# ===== PLOT =====
acc      = history.history['accuracy']      + history_fine.history['accuracy']
val_acc  = history.history['val_accuracy']  + history_fine.history['val_accuracy']
loss     = history.history['loss']          + history_fine.history['loss']
val_loss = history.history['val_loss']      + history_fine.history['val_loss']

# Mark the phase boundary
phase_boundary = len(history.history['accuracy'])

plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(acc,     label='Train Accuracy')
plt.plot(val_acc, label='Val Accuracy')
plt.axvline(x=phase_boundary, color='gray', linestyle='--', alpha=0.5, label='Fine-tune start')
plt.title('Accuracy')
plt.xlabel('Epoch')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(loss,     label='Train Loss')
plt.plot(val_loss, label='Val Loss')
plt.axvline(x=phase_boundary, color='gray', linestyle='--', alpha=0.5, label='Fine-tune start')
plt.title('Loss')
plt.xlabel('Epoch')
plt.legend()

plt.tight_layout()
plt.savefig("../model/training_plot.png")
plt.show()
print("✅ Training plot saved")