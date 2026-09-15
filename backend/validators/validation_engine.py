from backend.validators.blueprint_validator import validate_blueprint
from backend.validators.marks_validator import validate_marks
from backend.validators.structure_validator import validate_structure
from backend.validators.duplicate_validator import validate_duplicates
from backend.validators.similarity_validator import validate_similarity
from backend.validators.question_type_validator import validate_question_types

VALIDATORS = [
    validate_structure,
    validate_marks,
    validate_blueprint,
    validate_similarity,
    validate_duplicates,
    validate_question_types
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
        "warnings": [],
        "details": {}
    }

    reports = []

    for validator in VALIDATORS:
        if validator in (
            validate_structure,
            validate_marks,
            validate_question_types
        ):
            reports.append(
                validator(
                    generated_paper,
                    teacher_data
                )
            )
        elif validator in (
            validate_similarity,
            validate_blueprint
        ):
            reports.append(
                validator(
                    generated_paper,
                    exam_type,
                    subject
                )
            )
        else:
            reports.append(
                validator(
                    generated_paper
                )
            )

    for validator, result in zip(
        VALIDATORS,
        reports
    ):
        report["details"][
            validator.__name__
        ] = result

        if result.get("warnings"):
            report["warnings"].extend(
                result.get("warnings", [])
            )

        if not result.get("valid", False):
            report["valid"] = False
            report["errors"].extend(
                result.get("errors", [])
            )

    return report