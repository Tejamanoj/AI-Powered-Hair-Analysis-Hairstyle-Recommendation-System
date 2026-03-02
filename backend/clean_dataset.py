from PIL import Image
import os

dataset_path = "../datasets"
fixed = 0
removed = 0

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        path = os.path.join(root, file)

        try:
            img = Image.open(path)
            img = img.convert("RGB")   # force proper format
            img.save(path, "JPEG")     # rewrite file correctly
            fixed += 1
        except Exception:
            print("❌ Removing:", path)
            os.remove(path)
            removed += 1

print(f"\n✔ Fixed images: {fixed}")
print(f"❌ Removed images: {removed}")