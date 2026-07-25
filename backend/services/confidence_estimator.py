VALIDATOR_WEIGHTS = {

    "validate_structure": 35,

    "validate_marks": 25,

    "validate_blueprint": 15,

    "validate_similarity": 10,

    "validate_duplicates": 10,

    "validate_grammar": 5

}


def calculate_confidence(
        validation_report
):
    confidence= 100

    for validator, result in validation_report[
        "details"
    ].items():
        if not result["valid"]:
            confidence -= VALIDATOR_WEIGHTS.get(
                validator,
                0
            )

    confidence= max(
        confidence,
        0
    )

    return confidence