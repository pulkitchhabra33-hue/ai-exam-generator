from backend.services.generation_statistics import (
    build_generation_statistics
)

report = {

    "attempts": 3,

    "best_attempt": 2,

    "valid": False,

    "remaining_errors": 4

}

statistics = build_generation_statistics(

    report,

    quality_score=70,

    confidence="70%"

)

print()

print("=" * 60)

print("GENERATION STATISTICS")

print("=" * 60)

print()

for key, value in statistics.items():

    print(f"{key}: {value}")