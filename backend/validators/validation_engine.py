from backend.validators.blueprint_validator import validate_blueprint
from backend.validators.marks_validator import validate_marks
from backend.validators.structure_validator import validate_structure
from backend.validators.duplicate_validator import validate_duplicates
from backend.validators.grammar_validator import validate_grammar
from backend.validators.similarity_validator import validate_similarity

VALIDATORS= [
    validate_structure,
    validate_marks,
    validate_blueprint,
    validate_similarity,
    validate_duplicates,
]

def validate_generated_paper(
        generated_paper,
        teacher_data,
        exam_type,
        subject
):
    report= {
        "valid": True,
        "errors": [],
        "details": {}
    }

    reports= []

    for validator in VALIDATORS:
        if validator in (
            validate_structure,
            validate_marks
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


    for validator, result in zip(VALIDATORS, reports):
        report["details"][validator.__name__] = result
        if not result["valid"]:
            report["valid"] = False
            report["errors"].extend(
                result["errors"]
            )

    return report