from backend.services.teacher_summary import (
    build_teacher_summary
)

report = {

    "accepted": False,

    "quality_score": 58,

    "confidence": 62,

    "remaining_errors": 8,

    "reasons": [

        "Quality score below threshold.",

        "Too many validation errors."

    ]

}

summary = build_teacher_summary(
    report
)

print()

print("=" * 60)

print("TEACHER SUMMARY")

print("=" * 60)

print()

for key, value in summary.items():

    print(f"{key}: {value}")