from backend.services.feedback_builder import build_feedback
from backend.validators.validation_engine import validate_generated_paper
from backend.prompt_engine.regeneration_prompt import build_regeneration_prompt
from backend.services.ai_service import regenerate_paper
from backend.utils.logger import logger

MAX_REGENERATION_ATTEMPTS = 3

DEBUG_PROMPT = False


def iterative_generation(
        teacher_data,
        generated_paper,
        exam_type,
        subject
):

    best_paper = generated_paper
    best_validation = None
    lowest_errors = float("inf")
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
            f"VALIDATION ERRORS: {validation.get('errors', [])}"
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

        if current_errors < lowest_errors:

            lowest_errors = current_errors
            best_paper = best_paper
            best_validation = validation
            best_attempt = attempts_used

            logger.info(
                f"New Best Paper: "
                f"(Attempt {attempts_used}, "
                f"{current_errors} errors)"
            )

        if validation.get("valid"):

            logger.info(
                "Paper passed validation."
            )

            return {
                "paper": best_paper,
                "report": {
                    "attempts": attempts_used,
                    "best_attempt": best_attempt,
                    "valid": True,
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

        logger.info(
            f"Regenerated candidate validation errors: "
            f"{candidate_errors}"
        )

        if candidate_validation.get("valid"):

            logger.info(
                "Regenerated candidate passed validation."
            )

            return {
                "paper": candidate,
                "report": {
                    "attempts": attempts_used,
                    "best_attempt": attempts_used,
                    "valid": True,
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

        if candidate_errors < lowest_errors:

            best_paper = candidate
            best_validation = candidate_validation
            lowest_errors = candidate_errors
            best_attempt = attempts_used

            logger.info(
                f"Candidate became new best paper: "
                f"{candidate_errors} errors."
            )

        else:

            logger.info(
                f"Candidate rejected because it has "
                f"{candidate_errors} errors, while the best paper "
                f"has {lowest_errors} errors."
            )

    logger.error(
        "Unable to generate a valid exam paper "
        f"after {attempts_used} attempts."
    )

    logger.error(
        f"Best attempt: {best_attempt}"
    )

    logger.error(
        f"Remaining validation errors: {lowest_errors}"
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