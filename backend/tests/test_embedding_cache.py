from pathlib import Path

from backend.services.embedding_cache import (
    cache_repository_embeddings
)

cache_repository_embeddings(

    Path(
        "backend/generated_repository/science_repository.json"
    )

)

print("=" * 60)
print("EMBEDDING CACHE TEST")
print("=" * 60)
print()
print("Embeddings cached successfully.")