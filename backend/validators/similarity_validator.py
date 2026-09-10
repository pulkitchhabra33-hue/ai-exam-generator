from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.services.reference_retriever import retrieve_questions
from backend.utils.text_normalizer import normalize_question
from backend.utils.question_utils import build_question_id

SIMILARITY_THRESHOLD= 0.80

def get_question_text(question):
    parts= []

    question_text= question.get("question") or question.get("question_text")
    if question_text:
        parts.append(str(question_text))

    assertion= question.get("assertion")
    if assertion:
        parts.append(str(assertion))

    reason= question.get("reason")
    if reason:
        parts.append(str(reason))

    source= question.get("source")
    if source:
        parts.append(str(source))

    case= question.get("case")
    if case:
        parts.append(str(case))

    diagram= question.get("diagram")
    if diagram:
        parts.append(str(diagram))

    left_column= question.get("left_column")
    if isinstance(left_column, list):
        parts.extend(str(item) for item in left_column)

    right_column= question.get("right_column")
    if isinstance(right_column, list):
        parts.extend(str(item) for item in right_column)

    return " ".join(parts)

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

    reference_text= []

    for question in reference_questions:
        text= get_question_text(question)

        if text:
            reference_text.append(
                normalize_question(text)
            )

    if not reference_text:
        return report

    for section in generated_paper.get("sections", []):
        for index, question in enumerate(
                section.get("questions", []),
                start= 1
        ):
            generated_text= normalize_question(
                get_question_text(question)
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

            question_id= build_question_id(
                section,
                index
            )

            if max_similarity >= SIMILARITY_THRESHOLD:
                report["valid"]= False
                report["errors"].append(
                    f"Question {question_id} is too similar to "
                    f"reference question {best_match + 1} "
                    f"({max_similarity:.2%})."
                )

    return report