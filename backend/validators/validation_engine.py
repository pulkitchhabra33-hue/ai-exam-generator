from backend.validators.blueprint_validator import validate_blueprint
from backend.validators.marks_validator import validate_marks
from backend.validators.structure_validator import validate_structure
from backend.validators.duplicate_validator import validate_duplicates
from backend.validators.similarity_validator import validate_similarity
from backend.validators.question_type_validator import validate_question_types
from backend.validators.question_correctness_validator import validate_question_correctness

VALIDATORS = [
    validate_structure,
    validate_marks,
    validate_blueprint,
    validate_similarity,
    validate_duplicates,
    validate_question_types,
    validate_question_correctness
]


def validate_generated_paper(
    generated_paper,
    teacher_data,
    exam_type,
    subject
):
    report = {
        "valid": True,
        "errors": [],
        "details": {}
    }

    for validator in VALIDATORS:
        if validator in (
            validate_structure,
            validate_marks,
            validate_question_types,
            validate_question_correctness
        ):
            result = validator(
                generated_paper,
                teacher_data
            ) if validator is not validate_question_correctness else validator(
                generated_paper,
                exam_type,
                subject,
                teacher_data
            )
        elif validator in (
            validate_similarity,
            validate_blueprint
        ):
            result = validator(
                generated_paper,
                exam_type,
                subject
            )
        else:
            result = validator(generated_paper)

        report["details"][validator.__name__] = result

        if not result.get("valid", False):
            report["valid"] = False
            report["errors"].extend(
                result.get("errors", [])
            )

    return report