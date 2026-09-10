from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.utils.text_normalizer import normalize_question
from backend.utils.question_utils import build_question_id

DUPLICATE_THRESHOLD= 0.85

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

def validate_duplicates(
        generated_paper
):
    report= {
        "valid": True,
        "errors": []
    }

    questions= []
    question_numbers= []

    for section in generated_paper.get("sections", []):
        for index, question in enumerate(
                section.get("questions", []),
                start= 1
        ):
            text= normalize_question(
                get_question_text(question)
            ).strip()

            question_id= build_question_id(
                section,
                index
            )

            if text:
                questions.append(text)
                question_numbers.append(
                    question_id
                )

    if len(questions)<2:
        return report

    vectorizer= TfidfVectorizer()
    vectors= vectorizer.fit_transform(
        questions
    )

    similarity_matrix= cosine_similarity(
        vectors
    )

    for i in range(len(questions)):
        for j in range(i + 1, len(questions)):
            similarity= similarity_matrix[i][j]

            if similarity >= DUPLICATE_THRESHOLD:
                report["valid"]= False
                report["errors"].append(
                    f"Question {question_numbers[i]} and "
                    f"Question {question_numbers[j]} appear to be "
                    f"duplicates ({similarity:.2%})."
                )

    return report