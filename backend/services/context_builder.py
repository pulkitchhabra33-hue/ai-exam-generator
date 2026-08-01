from backend.services.semantic_search import semantic_search
from backend.services.diversity_engine import diversify_results
from backend.services.batch_question_rewriter import rewrite_questions

def build_generation_context (
        query,
        repository,
        teacher_requirements
):
    ranked= semantic_search(
        query= query,
        repository= repository,
        teacher_requirements= teacher_requirements,
        top_k= 20
    )

    selected= diversify_results(
        ranked_results= ranked,
        top_k= 10
    )

    questions= []

    for _, question in selected:
        questions.append(
            {
                "question": question["question"]
            }
        )

    rewritten= rewrite_questions(
        questions,
        teacher_requirements
    )

    return rewritten