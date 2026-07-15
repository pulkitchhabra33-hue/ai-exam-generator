from backend.services.pattern_analyzer import analyze_patterns

def normalize_distribution(counter):

    if not hasattr(counter, "values"):
        raise TypeError(
            "normalize_distribution expects a dictionary or Counter."
        )

    total = sum(counter.values())

    if total == 0:
        return {}

    return {
        key: value / total
        for key, value in counter.items()
    }


def get_expected_blueprint(exam_type, subject):
    analysis= analyze_patterns(
        exam_type,
        subject
    )

    #If repository has papers, use repository statistics
    if analysis["paper_count"] > 0:
        return {
            "difficulty_distribution": normalize_distribution(analysis["difficulty_distribution"]),
            "cognitive_distribution": normalize_distribution(analysis["cognitive_distribution"]),
            "question_type_distribution": normalize_distribution(analysis["question_type_distribution"]),
            "chapter_distribution": normalize_distribution(analysis["chapter_distribution"])
        }
    

     # -------------------------
    # Fallback (Board Defaults)
    # -------------------------

    # Later we'll replace this
    # with CBSE / ICSE files.

    return {

        "difficulty_distribution": {
            "Easy": 0.30,
            "Medium": 0.50,
            "Hard": 0.20
        },

        "cognitive_distribution": {
            "Recall": 0.30,
            "Understanding": 0.40,
            "Application": 0.20,
            "Analysis": 0.10
        },

        "question_type_distribution": {},

        "chapter_distribution": {}

    }