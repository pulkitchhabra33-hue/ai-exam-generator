from backend.services.feedback_builder import build_feedback
from backend.validators.validation_engine import validate_generated_paper
from backend.prompt_engine.regeneration_prompt import build_regeneration_prompt
from backend.services.ai_service import regenerate_paper
from backend.utils.logger import logger

import time

MAX_REGENERATION_ATTEMPTS= 1

DEBUG_PROMPT = False

def iterative_generation(
        teacher_data,
        generated_paper,
        exam_type,
        subject
):
    
    best_paper= generated_paper
    best_validation= None
    lowest_errors= float("inf")
    best_attempt= 0

    attempts_used= 0

    for attempt in range(MAX_REGENERATION_ATTEMPTS):
        attempts_used= attempt + 1

        print(f"[GEN] before validation", flush= True)

        validation_start= time.time()

        validation= validate_generated_paper(
            generated_paper,
            teacher_data,
            exam_type,
            subject
        )
        print(f"[GEN] after validation - took {time.time() - validation_start:.2f} seconds", flush=True)

        current_errors= len(
            validation["errors"]
        )

        if current_errors < lowest_errors:
            lowest_errors= current_errors
            best_paper= generated_paper
            best_validation= validation

            best_attempt= attempt + 1


            logger.info(
                f"New Best Paper: (Attempt {attempt + 1}, {current_errors} errors)"
            )

        if validation["valid"]:
            logger.info(
                "Paper passed validation."
            )

            return {

                "paper": generated_paper,

                "report": "validation",
                "statistics": {
                    "attempts": attempts_used,
                    "best_attempt": attempt + 1,
                    "remaining_errors": 0
                }
            }
        
        feedback= build_feedback(
            validation
        )

        prompt= build_regeneration_prompt(
            teacher_data,
            generated_paper,
            feedback
        )


        print("=" * 60)
        logger.info(f"Regeneration Attempt {attempt + 1}")
        print("=" * 60)

        print("Feedback:")

        for item in feedback:
            print("-", item)

        print()
        
        print(f"Feedback Items: {len(feedback)}")
        print(f"Prompt Length: {len(prompt)} characters")

        if DEBUG_PROMPT:
            print()
            print("=" * 60)
            print("REGENERATION PROMPT")
            print("=" * 60)
            print(prompt)

        generated_paper = regenerate_paper(prompt)
        
        if "error" in generated_paper:

            logger.error("Regeneration failed.")

            logger.error(generated_paper["error"])

            return generated_paper
        

    print("=" * 60)
    logger.info("Returning Best Paper")
    print("=" * 60)

    print()
    print(f"Remaining Errors: {lowest_errors}")
    print(f"Best Attempt: {best_attempt}")

    if best_validation:
        print(
            f"Best Validation Errors: {len(best_validation['errors'])}"
        )

    return {

        "paper": best_paper,

        "report": best_validation,
        "statistics": {
            "attempts": attempts_used,
            "best_attempt": best_attempt,
            "remaining_errors": lowest_errors,
        }   
    }