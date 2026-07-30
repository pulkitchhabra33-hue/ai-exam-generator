from pathlib import Path

from backend.services.file_service import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    UPLOAD_FOLDER
)

print("=" * 60)
print("FILE UPLOAD SERVICE TEST")
print("=" * 60)

print()

print("Upload Folder Exists:")
print(UPLOAD_FOLDER.exists())

print()

print("Upload Folder:")
print(UPLOAD_FOLDER)

print()

print("Allowed Extensions:")
for extension in sorted(ALLOWED_EXTENSIONS):
    print("-", extension)

print()

print("Maximum File Size:")
print(f"{MAX_FILE_SIZE / (1024 * 1024)} MB")

print()

print("Directory Contents:")

files = list(
    Path(UPLOAD_FOLDER).glob("*")
)

if not files:
    print("No uploaded files.")

else:
    for file in files:
        print("-", file.name)