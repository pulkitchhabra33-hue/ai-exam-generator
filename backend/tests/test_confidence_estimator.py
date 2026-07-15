from backend.services.confidence_estimator import (
    calculate_confidence
)

validation = {

    "details": {

        "validate_structure": {
            "valid": True
        },

        "validate_marks": {
            "valid": True
        },

        "validate_blueprint": {
            "valid": False
        },

        "validate_similarity": {
            "valid": True
        },

        "validate_duplicates": {
            "valid": False
        },

        "validate_grammar": {
            "valid": False
        }

    }

}

confidence = calculate_confidence(
    validation
)

print()

print("=" * 60)

print("CONFIDENCE ESTIMATION")

print("=" * 60)

print()

print(confidence)