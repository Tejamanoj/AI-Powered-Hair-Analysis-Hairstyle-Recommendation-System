# deep_clean.py
import os
from PIL import Image

dataset_dir = "../datasets"
removed = 0
fixed = 0

for root, dirs, files in os.walk(dataset_dir):
    for fname in files:
        fpath = os.path.join(root, fname)
        try:
            img = Image.open(fpath)
            img.verify()  # checks integrity without fully loading

            # Re-open after verify (verify() leaves file in unusable state)
            img = Image.open(fpath)
            img = img.convert("RGB")  # ensures it's a valid RGB image TF can read

            # Re-save as proper JPEG to fix any format quirks
            img.save(fpath, "JPEG", quality=95)
            fixed += 1

        except Exception as e:
            print(f"Removing bad file: {fpath} — {e}")
            os.remove(fpath)
            removed += 1

print(f"\n✔ Re-saved: {fixed}")
print(f"❌ Removed: {removed}")