from backend.services.feedback_builder import build_feedback
from backend.validators.validation_engine import validate_generated_paper
from backend.prompt_engine.regeneration_prompt import build_regeneration_prompt
from backend.services.ai_service import regenerate_paper
from backend.utils.logger import logger


MAX_REGENERATION_ATTEMPTS = 5

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
            generated_paper,
            teacher_data,
            exam_type,
            subject
        )

        current_errors = len(
            validation["errors"]
        )

        if current_errors < lowest_errors:

            lowest_errors = current_errors
            best_paper = generated_paper
            best_validation = validation
            best_attempt = attempt + 1

            logger.info(
                f"New Best Paper: "
                f"(Attempt {attempt + 1}, "
                f"{current_errors} errors)"
            )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if validation["valid"]:

            logger.info(
                "Paper passed validation."
            )

            return {
                "paper": generated_paper,
                "report": {
                    "attempts": attempts_used,
                    "best_attempt": attempt + 1,
                    "valid": True,
                    "remaining_errors": 0,
                    "validators": validation["details"]
                },
                "statistics": {
                    "attempts": attempts_used,
                    "best_attempt": attempt + 1,
                    "remaining_errors": 0
                }
            }

        # --------------------------------------------------
        # REGENERATION
        # --------------------------------------------------

        feedback = build_feedback(
            validation
        )

        prompt = build_regeneration_prompt(
            teacher_data,
            generated_paper,
            feedback
        )

        logger.info(
            f"Regeneration Attempt {attempt + 1}"
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

            logger.info(prompt)

        generated_paper = regenerate_paper(
            prompt
        )

        # --------------------------------------------------
        # REGENERATION API FAILURE
        # --------------------------------------------------

        if not isinstance(
            generated_paper,
            dict
        ):

            logger.error(
                "Regeneration returned invalid data."
            )

            continue

        if "error" in generated_paper:

            logger.error(
                "Regeneration failed."
            )

            logger.error(
                generated_paper["error"]
            )

            continue

    # ------------------------------------------------------
    # ALL ATTEMPTS FAILED
    # ------------------------------------------------------

    logger.error(
        "Unable to generate a valid exam paper "
        f"after {attempts_used} attempts."
    )

    logger.error(
        f"Best attempt: {best_attempt}"
    )

    logger.error(
        f"Remaining validation errors: "
        f"{lowest_errors}"
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