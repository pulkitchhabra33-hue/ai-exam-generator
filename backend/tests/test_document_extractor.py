from pathlib import Path

from backend.services.document_extractor import (
    extract_text
)

print("=" * 60)
print("DOCUMENT EXTRACTOR TEST")
print("=" * 60)

print()

file_path = Path(
    "backend/uploads/temp/sample.pdf"
)

if not file_path.exists():
    print("Place a sample.pdf file in:")
    print(file_path.parent)
else:
    text = extract_text(file_path)

    print("Characters Extracted:")
    print(len(text))

    print()

    print("First 1000 Characters:\n")

    print(text[:1000])