from backend.metadata_engine.service_ai import get_metadata
from backend.metadata_engine.merger import merge_metadata

def generate_metadata(blueprint):
    metadata= get_metadata(blueprint)
    enriched_metadata= merge_metadata(blueprint, metadata)
    
    return enriched_metadata