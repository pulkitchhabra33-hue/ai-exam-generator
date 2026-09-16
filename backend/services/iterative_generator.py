from backend.services.feedback_builder import build_feedback
from backend.validators.validation_engine import validate_generated_paper
from backend.prompt_engine.regeneration_prompt import build_regeneration_prompt
from backend.services.ai_service import regenerate_paper
from backend.utils.logger import logger

MAX_REGENERATION_ATTEMPTS = 3
DEBUG_PROMPT = False


def validation_score(validation):
    details = validation.get("details", {})
    errors = validation.get("errors", [])

    weights = {
        "validate_structure": 1000,
        "validate_marks": 1000,
        "validate_question_types": 1000,
        "validate_blueprint": 100,
        "validate_similarity": 50,
        "validate_duplicates": 50
    }

    score = 0

    for validator_name, validator_result in details.items():
        error_count = len(
            validator_result.get("errors", [])
        )

        score += error_count * weights.get(
            validator_name,
            10
        )

    score += len(errors)

    return score


def iterative_generation(
        teacher_data,
        generated_paper,
        exam_type,
        subject
):

    if not isinstance(generated_paper, dict):
        logger.error(
            "Initial generated paper is not a valid dictionary."
        )

        return {
            "success": False,
            "error": "Initial generated paper is invalid.",
            "stage": "iterative_generation"
        }

    if "error" in generated_paper:
        logger.error(
            "Initial AI generation failed."
        )

        logger.error(
            generated_paper.get("error")
        )

        return {
            "success": False,
            "error": generated_paper.get(
                "error",
                "Initial AI generation failed."
            ),
            "stage": "iterative_generation"
        }

    if "sections" not in generated_paper:
        logger.error(
            "Initial generated paper has no sections."
        )

        return {
            "success": False,
            "error": "Initial generated paper has no sections.",
            "stage": "iterative_generation"
        }

    best_paper = generated_paper
    best_validation = None
    best_score = float("inf")
    best_attempt = 0
    attempts_used = 0

    for attempt in range(MAX_REGENERATION_ATTEMPTS):

        attempts_used = attempt + 1

        validation = validate_generated_paper(
            best_paper,
            teacher_data,
            exam_type,
            subject
        )

        logger.info(
            f"VALIDATION ERRORS: "
            f"{validation.get('errors', [])}"
        )

        for validator_name, validator_result in validation.get(
                "details",
                {}
        ).items():

            logger.info(
                f"{validator_name}: "
                f"{len(validator_result.get('errors', []))} errors"
            )

        current_errors = len(
            validation.get("errors", [])
        )

        current_score = validation_score(
            validation
        )

        if current_score < best_score:

            best_score = current_score
            best_validation = validation
            best_attempt = attempts_used

            logger.info(
                f"New Best Paper: "
                f"(Attempt {attempts_used}, "
                f"{current_errors} errors, "
                f"score {current_score})"
            )

        if validation.get("valid"):

            logger.info(
                "Paper passed validation."
            )

            return {
                "paper": best_paper,
                "report": {
                    "valid": True,
                    "errors": validation.get(
                        "errors",
                        []
                    ),
                    "details": validation.get(
                        "details",
                        {}
                    ),
                    "attempts": attempts_used,
                    "best_attempt": best_attempt,
                    "remaining_errors": 0,
                    "validators": validation.get(
                        "details",
                        {}
                    )
                },
                "statistics": {
                    "attempts": attempts_used,
                    "best_attempt": best_attempt,
                    "remaining_errors": 0
                }
            }

        feedback = build_feedback(
            validation
        )

        if current_errors >= 2:
            logger.info(
                "Multiple validation errors detected. "
                "Regeneration will repair the existing paper "
                "with targeted changes instead of regenerating "
                "the paper from scratch."
            )

        prompt = build_regeneration_prompt(
            teacher_data,
            best_paper,
            feedback
        )

        logger.info(
            f"Regeneration Attempt {attempts_used}"
        )

        logger.info(
            f"Feedback Items: {len(feedback)}"
        )

        logger.info(
            f"Prompt Length: {len(prompt)} characters"
        )

        if DEBUG_PROMPT:

            logger.info(
                "REGENERATION PROMPT"
            )

            logger.info(
                prompt
            )

        candidate = regenerate_paper(
            prompt
        )

        if not isinstance(
            candidate,
            dict
        ):

            logger.error(
                "Regeneration returned invalid data."
            )

            continue

        if "error" in candidate:

            logger.error(
                "Regeneration failed."
            )

            logger.error(
                candidate["error"]
            )

            continue

        if "sections" not in candidate:

            logger.error(
                "Regeneration returned a paper without sections."
            )

            continue

        candidate_validation = validate_generated_paper(
            candidate,
            teacher_data,
            exam_type,
            subject
        )

        candidate_errors = len(
            candidate_validation.get(
                "errors",
                []
            )
        )

        candidate_score = validation_score(
            candidate_validation
        )

        logger.info(
            f"Regenerated candidate validation errors: "
            f"{candidate_errors}"
        )

        logger.info(
            f"Regenerated candidate validation score: "
            f"{candidate_score}"
        )

        if candidate_validation.get("valid"):

            logger.info(
                "Regenerated candidate passed validation."
            )

            return {
                "paper": candidate,
                "report": {
                    "valid": True,
                    "errors": candidate_validation.get(
                        "errors",
                        []
                    ),
                    "details": candidate_validation.get(
                        "details",
                        {}
                    ),
                    "attempts": attempts_used,
                    "best_attempt": attempts_used,
                    "remaining_errors": 0,
                    "validators": candidate_validation.get(
                        "details",
                        {}
                    )
                },
                "statistics": {
                    "attempts": attempts_used,
                    "best_attempt": attempts_used,
                    "remaining_errors": 0
                }
            }

        best_errors = len(
            best_validation.get("errors", [])
        ) if best_validation else current_errors

        if candidate_score < best_score:

            best_paper = candidate
            best_validation = candidate_validation
            best_score = candidate_score
            best_attempt = attempts_used

            logger.info(
                f"Candidate became new best paper: "
                f"{candidate_errors} errors, "
                f"score {candidate_score}."
            )

        else:

            logger.info(
                f"Candidate rejected because its validation score "
                f"({candidate_score}) is not better than the best score "
                f"({best_score})."
            )

    logger.error(
        "Unable to generate a valid exam paper "
        f"after {attempts_used} attempts."
    )

    logger.error(
        f"Best attempt: {best_attempt}"
    )

    remaining_errors = len(
        best_validation.get("errors", [])
    ) if best_validation else 0

    logger.error(
        f"Remaining validation errors: {remaining_errors}"
    )

    return {
        "success": False,
        "error": (
            "Unable to generate a valid exam paper "
            "after multiple attempts."
        ),
        "stage": "iterative_generation",
        "attempts": attempts_used
    }