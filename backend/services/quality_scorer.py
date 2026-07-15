VALIDATOR_WEIGHTS= {
    "validate_structure": 35,
    "validate_marks": 25,
    "validate_blueprint": 15,
    "validate_similarity": 10,
    "validate_duplicates": 10,
    "validate_grammar": 5
}


def calculate_quality_score(
        validation_report
):
    score= 100

    for validator, result in validation_report[
        "details"
    ].items():
        if not result["valid"]:
            score -= VALIDATOR_WEIGHTS.get(
                validator,
                0
            )

    score= max(
        score, 
        0
    )

    return score