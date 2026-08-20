from backend.services.generation_pipeline import generate_exam_paper

def create_exam_paper(teacher_data):
    """
    Main application-level entry point for exam paper creation.
    This function acts as the bridge between the API layer
    and the AI generation pipeline.
    """

    result= generate_exam_paper(teacher_data)

    if not result["success"]:
        return result

    return result