import time

from backend.services.ai_service import generate_paper
from backend.services.iterative_generator import iterative_generation
from backend.services.quality_scorer import calculate_quality_score
from backend.services.confidence_estimator import calculate_confidence
from backend.services.generation_statistics import build_generation_statistics
from backend.services.acceptance_engine import should_accept
from backend.services.teacher_summary import build_teacher_summary
from backend.services.final_result_builder import build_final_result
from backend.utils.logger import logger


def generate_exam_paper(teacher_data):
    try:
        pipeline_start= time.perf_counter()

        generation_start= time.perf_counter()

        paper= generate_paper(teacher_data)

        generation_time= (
            time.perf_counter()
            - generation_start
        )

        validation_start= time.perf_counter()

        result= iterative_generation(
            teacher_data,
            paper,
            teacher_data["exam_type"],
            teacher_data["subject"]
        )

        validation_time= (
            time.perf_counter()
            - validation_start
        )

        pipeline_time= (
            time.perf_counter()
            - pipeline_start
        )

        paper= result["paper"]

        validation_report= result["report"]
        generation_statistics= result["statistics"]

        quality= calculate_quality_score(validation_report)
        confidence= calculate_confidence(validation_report)

        statistics= build_generation_statistics(
            validation_report,
            generation_statistics,
            quality,
            confidence
        )

        statistics["generation_time"]= round(generation_time, 2)
        statistics["validation_time"]= round(validation_time, 2)
        statistics["pipeline_time"]= round(pipeline_time, 2)

        acceptance= should_accept(statistics)
        summary= build_teacher_summary(acceptance)

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

    except Exception as error:

        logger.exception(
            f"Generation Pipeline Error: {error}"
        )
        
        return {
            "success": False,
            "error": str(error),
            "stage": "generation_pipeline"
        }