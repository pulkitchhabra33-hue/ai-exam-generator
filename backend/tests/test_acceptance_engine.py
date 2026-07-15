from backend.services.acceptance_engine import (
    should_accept
)

statistics = {

    "quality_score": 55,

    "confidence": "62%",

    "remaining_errors": 11

}

decision = should_accept(
    statistics
)

print()

print("=" * 60)

print("PAPER ACCEPTANCE")

print("=" * 60)

print()

for key, value in decision.items():

    print(f"{key}: {value}")