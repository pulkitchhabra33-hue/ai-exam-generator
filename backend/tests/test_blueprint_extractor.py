from backend.services.blueprint_extractor import (
    build_blueprint
)

questions = [

    "1. Define Ohm's Law. (2)",

    "2. Explain Photosynthesis. (5)",

    """3. Assertion:
Reason:
(1)""",

    "4. Calculate the current. (2)"

]

blueprint = build_blueprint(
    questions
)

print("=" * 60)
print("BLUEPRINT EXTRACTION TEST")
print("=" * 60)

print()

for key, value in blueprint.items():

    print(f"{key}: {value}")