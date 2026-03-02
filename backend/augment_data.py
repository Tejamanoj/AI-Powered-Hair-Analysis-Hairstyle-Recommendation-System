import tensorflow as tf
import numpy as np
from PIL import Image
import os

# ===== SETTINGS =====
dataset_path = "../datasets"
TARGET_COUNT = 600  # We want 600 images per class

# ===== ALL 11 CLASSES =====
all_classes = ['Straight', 'Wavy', 'bald', 'curly', 'dreadlocks',
               'dry', 'frizzy', 'hairfall', 'healthy', 'kinky', 'notbald']

# ===== AUGMENTATION =====
def augment_image(img):
    img = tf.image.random_flip_left_right(img)
    img = tf.image.random_brightness(img, 0.25)
    img = tf.image.random_contrast(img, 0.75, 1.25)
    img = tf.image.random_saturation(img, 0.75, 1.25)
    img = tf.image.random_hue(img, 0.1)
    img = tf.clip_by_value(img, 0, 255)
    return img

# ===== PROCESS EACH CLASS =====
print("===== AUGMENTATION =====\n")

for class_name in all_classes:
    class_path = os.path.join(dataset_path, class_name)

    if not os.path.exists(class_path):
        print(f"⚠️  Skipping {class_name} — folder not found")
        continue

    # Only count REAL images (not previously augmented ones)
    images = [f for f in os.listdir(class_path)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))
              and not f.startswith('aug_')]

    current_count = len(images)
    total_count = len([f for f in os.listdir(class_path)
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    print(f"{class_name}: {current_count} real images, {total_count} total → target {TARGET_COUNT}")

    if total_count >= TARGET_COUNT:
        print(f"  ✅ Already at target — skipping\n")
        continue

    needed = TARGET_COUNT - total_count
    print(f"  📸 Generating {needed} augmented images...")

    count = 0
    while count < needed:
        src_img_name = images[count % current_count]
        src_img_path = os.path.join(class_path, src_img_name)

        try:
            img = Image.open(src_img_path).convert("RGB").resize((224, 224))
            img_array = tf.cast(np.array(img), tf.float32)
            augmented = augment_image(img_array).numpy().astype(np.uint8)

            new_img = Image.fromarray(augmented)
            new_name = f"aug_{count}_{src_img_name}"
            new_img.save(os.path.join(class_path, new_name))
            count += 1

        except Exception as e:
            print(f"  ⚠️  Skipping {src_img_name}: {e}")
            continue

    print(f"  ✅ Done! {class_name} now has {TARGET_COUNT} images\n")

# ===== FINAL SUMMARY =====
print("\n===== FINAL COUNTS =====")
for class_name in all_classes:
    class_path = os.path.join(dataset_path, class_name)
    if os.path.exists(class_path):
        count = len([f for f in os.listdir(class_path)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        status = "✅" if count >= TARGET_COUNT else "⚠️ "
        print(f"  {status} {class_name}: {count} images")

print("\n🎉 Augmentation complete! Ready to retrain.")