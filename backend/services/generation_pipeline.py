import time

from backend.services.ai_service import generate_paper
from backend.services.iterative_generator import iterative_generation
from backend.services.quality_scorer import calculate_quality_score
from backend.services.confidence_estimator import calculate_confidence
from backend.services.generation_statistics import build_generation_statistics
from backend.services.acceptance_engine import should_accept
from backend.services.teacher_summary import build_teacher_summary
from backend.validators.content_quality_validator import validate_and_repair_paper
from backend.services.final_result_builder import build_final_result
from backend.utils.logger import logger

MAX_PIPELINE_TIME = 150

def check_pipeline_timeout(
        pipeline_start
):
    elapsed = (
        time.perf_counter()
        - pipeline_start
    )

    if elapsed >= MAX_PIPELINE_TIME:
        raise TimeoutError(
            "Exam generation took too long."
            "Please try again."
        )

def generate_exam_paper(
        teacher_data
):
    pipeline_start = time.perf_counter()

    try:
        generation_start = time.perf_counter()

        paper = generate_paper(
            teacher_data
        )

        generation_time = (
            time.perf_counter()
            - generation_start
        )

        validation_start = time.perf_counter()

        result = iterative_generation(
            teacher_data,
            paper,
            teacher_data["exam_type"],
            teacher_data["subject"]
        )

        check_pipeline_timeout(
            pipeline_start
        )

        validation_time = (
            time.perf_counter()
            - validation_start
        )

        pipeline_time = (
            time.perf_counter()
            - pipeline_start
        )

        paper = result["paper"]

        validation_report = result["report"]

        generation_statistics = result[
            "statistics"
        ]

        logger.info(
            "Starting final content quality audit."
        )

        quality_start = time.perf_counter()

        paper, content_quality_report = (
            validate_and_repair_paper(
                paper,
                teacher_data
            )
        )

        quality_time = (
            time.perf_counter()
            - quality_start
        )

        validation_report.setdefault(
            "details",
            {}
        )

        validation_report["details"][
            "validate_content_quality"
        ] = content_quality_report

        validation_report.setdefault(
            "warnings",
            []
        )

        content_warnings = (
            content_quality_report.get(
                "warnings",
                []
            )
        )

        if content_warnings:
            validation_report[
                "warnings"
            ].extend(
                content_warnings
            )

            logger.warning(
                "Content quality warnings: "
                f"{content_warnings}"
            )

        if not content_quality_report.get(
            "valid",
            False
        ):
            hard_errors = (
                content_quality_report.get(
                    "errors",
                    []
                )
            )

            logger.error(
                "Confirmed HARD content quality "
                "failures: "
                f"{hard_errors}"
            )

            return {
                "success": False,
                "error": (
                    "The generated paper failed "
                    "final academic quality validation."
                ),
                "stage": (
                    "content_quality_validation"
                )
            }

        logger.info(
            "Final content quality validation passed."
        )

        quality = calculate_quality_score(
            validation_report
        )

        confidence = calculate_confidence(
            validation_report
        )

        statistics = build_generation_statistics(
            validation_report,
            generation_statistics,
            quality,
            confidence
        )

        statistics[
            "generation_time"
        ] = round(
            generation_time,
            2
        )

        statistics[
            "validation_time"
        ] = round(
            validation_time,
            2
        )

        statistics[
            "pipeline_time"
        ] = round(
            pipeline_time,
            2
        )

        statistics[
            "content_quality_time"
        ] = round(
            quality_time,
            2
        )

        acceptance = should_accept(
            statistics
        )

        summary = build_teacher_summary(
            acceptance
        )

        logger.info(
            "Exam paper generated successfully."
        )

        return {
            "success": True,
            "result": build_final_result(
                paper,
                statistics,
                acceptance,
                summary
            )
        }

    except TimeoutError as error:
        elapsed = (
            time.perf_counter()
            - pipeline_start
        )

        logger.error(
            f"Generation pipeline timeout "
            f"after {round(elapsed, 2)} seconds."
        )

        return {
            "success": False,
            "error": (
                "Exam generation took too long. "
                "Please try again."
            ),
            "stage": "generation_pipeline",
            "timeout": True
        }

    except Exception as error:
        logger.exception(
            f"Generation Pipeline Error: {error}"
        )

        return {
            "success": False,
            "error": str(error),
            "stage": "generation_pipeline"
        }