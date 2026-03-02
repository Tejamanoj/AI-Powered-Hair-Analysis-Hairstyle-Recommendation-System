# Save this as backend/clean_all.py
from PIL import Image
import os

dataset_path = "../datasets"
removed = 0
fixed = 0

for class_name in os.listdir(dataset_path):
    class_path = os.path.join(dataset_path, class_name)
    if not os.path.isdir(class_path):
        continue

    print(f"\nCleaning {class_name}...")

    for fname in os.listdir(class_path):
        fpath = os.path.join(class_path, fname)
        try:
            img = Image.open(fpath)
            img.verify()
            img = Image.open(fpath).convert("RGB")
            img.save(fpath, "JPEG", quality=95)
            fixed += 1
        except Exception as e:
            print(f"  ❌ Removing: {fname} — {e}")
            os.remove(fpath)
            removed += 1

print(f"\n✅ Fixed: {fixed}")
print(f"❌ Removed: {removed}")