from backend.exam_patterns.blueprints import get_cognitive_blueprint

def allocate_questions(exam_type, total_questions):
    """
    Returns question allocation plan
    based on cognitive blueprint.
    """

    cognitive_blueprint= get_cognitive_blueprint(exam_type)

    recall= round(total_questions*cognitive_blueprint / 100)
    understanding= round(total_questions*cognitive_blueprint / 100)
    application= round(total_questions*cognitive_blueprint / 100)
    analysis= (
        total_questions
        -recall
        -understanding
        -application
               )
    
    return {
        "recall": recall,
        "understanding": understanding,
        "application": application,
        "analysis": analysis
    }