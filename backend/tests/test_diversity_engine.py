from backend.services.diversity_engine import (
    diversify_results
)

results = [

    (0.95, {"question":"Explain Ohm's Law"}),

    (0.94, {"question":"State Ohm's Law"}),

    (0.93, {"question":"Derive Ohm's Law"}),

    (0.91, {"question":"Resistance"}),

    (0.90, {"question":"Current"}),

    (0.88, {"question":"Power"}),

    (0.87, {"question":"Circuits"}),

    (0.85, {"question":"Kirchhoff"}),

    (0.83, {"question":"Electric Field"}),

    (0.81, {"question":"Potential Difference"})

]

diverse = diversify_results(
    results,
    top_k=5
)

print("=" * 60)
print("DIVERSITY ENGINE TEST")
print("=" * 60)

print()

for score, question in diverse:

    print(

        round(score,3),

        "-",

        question["question"]

    )