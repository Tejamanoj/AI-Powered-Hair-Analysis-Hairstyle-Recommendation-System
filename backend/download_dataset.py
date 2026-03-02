import kagglehub
import os

# Download dataset
print("Downloading dataset...")
path = kagglehub.dataset_download("kavyasreeb/hair-type-dataset")
print("Downloaded to:", path)

# Show what's inside
for root, dirs, files in os.walk(path):
    level = root.replace(path, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    if level < 2:
        subindent = ' ' * 2 * (level + 1)
        for file in files[:3]:
            print(f'{subindent}{file}')