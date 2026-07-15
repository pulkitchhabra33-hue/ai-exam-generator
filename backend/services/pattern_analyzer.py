from backend.services.knowledge_builder import build_knowledge

def top_items(counter, limit= 5):
        items= sorted(
            counter.items(),
            key= lambda item: item[1],
            reverse= True
        )

        return [
            name for name, _ in items[:limit]
        ]

def analyze_patterns(exam_type, subject):
    knowledge= build_knowledge(exam_type, subject)

    analysis= {
        "paper_count": knowledge["papers"],
        "total_questions": knowledge["total_questions"],
        "top_question_types": top_items(knowledge["question_types"]),
        "question_type_distribution": knowledge["question_types"],
        "top_chapters": top_items(knowledge["chapters"]),
        "top_concepts": top_items(knowledge["concepts"]),
        "chapter_distribution": knowledge["chapters"],
        "concept_distribution": knowledge["concepts"],
        "difficulty_distribution": knowledge["difficulty"],
        "cognitive_distribution": knowledge["cognitive"]
    }

    return analysis