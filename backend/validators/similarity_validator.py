from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.services.reference_retriever import retrieve_questions
from backend.utils.text_normalizer import normalize_question
from backend.utils.question_utils import build_question_id

SIMILARITY_THRESHOLD= 0.80


def validate_similarity(
        generated_paper,
        exam_type,
        subject
):
    report= {
        "valid": True,
        "errors": []
    }

    reference_questions= retrieve_questions(
        exam_type,
        subject,
        {}
    )

    reference_text= [
        normalize_question(question["question_text"])
        for question in reference_questions
    ]

    if not reference_text:
        return report

    for section in generated_paper.get("sections", []):
        for index, question in enumerate(section.get("questions", []), start= 1):
            generated_text= normalize_question(
                question.get(
                    "question_text",
                    ""
                )
            )

            if not generated_text:
                continue


            documents= reference_text + [
                generated_text
            ]

            vectorizer= TfidfVectorizer()
            vectors= vectorizer.fit_transform(
                documents
            )

            reference_vectors= vectors[:-1]
            generated_vector= vectors[-1]

            scores= cosine_similarity(
                generated_vector,
                reference_vectors
            )

            max_similarity= scores.max()
            best_match= scores.argmax()

            question_id = build_question_id(
                section,
                index
            )

            if max_similarity >= SIMILARITY_THRESHOLD:
                report["valid"] = False
                report["errors"].append(
                    f"Question {question_id} is too similar to reference question "
                    f"{best_match + 1} ({max_similarity:.2%})."
                )

    return report