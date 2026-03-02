from PIL import Image
import os

dataset_path = "datasets"

bad_files = []

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        path = os.path.join(root, file)

        try:
            img = Image.open(path)
            img.verify()   # verify image
        except Exception:
            print("❌ Removing bad file:", path)
            bad_files.append(path)

# delete bad files
for file in bad_files:
    os.remove(file)

print("\nDone. Removed", len(bad_files), "bad images.")