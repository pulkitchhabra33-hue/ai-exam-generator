from backend.services.final_result_builder import (
    build_final_result
)

paper = {

    "sections": []

}

statistics = {

    "attempts": 2,

    "quality_score": 88

}

acceptance = {

    "accepted": True

}

summary = {

    "status": "Ready for Download"

}

result = build_final_result(

    paper,

    statistics,

    acceptance,

    summary

)

print()

print("=" * 60)

print("FINAL RESULT")

print("=" * 60)

print()

for key, value in result.items():

    print(f"{key}: {value}")