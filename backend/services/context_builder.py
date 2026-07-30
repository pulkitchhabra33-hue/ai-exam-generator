from backend.services.semantic_search import semantic_search
from backend.services.diversity_engine import diversify_results
from backend.services.question_rewriter import rewrite_question

def build_generation_context (
        query,
        repository,
        teacher_requirements
):
    ranked= semantic_search(
        query= query,
        repository= repository,
        top_k= 20
    )

    selected= diversify_results(
        ranked_results= ranked,
        top_k= 10
    )

    rewritten= []

    for _, question in selected:
        rewritten.append(
            rewrite_question(
                question["question"],
                teacher_requirements
            )
        )

    return rewritten