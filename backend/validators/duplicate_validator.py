from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.utils.text_normalizer import normalize_question
from backend.utils.question_utils import build_question_id

# Higher threshold because we're comparing
# questions within the same generated paper.
# Only near-identical questions should be flagged.

DUPLICATE_THRESHOLD= 0.85

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
        for index, question in enumerate(section.get("questions", []), start= 1):
            text= normalize_question(question.get("question_text", "")).strip()


            question_id = build_question_id(
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
    vectors= vectorizer.fit_transform(questions)

    similarity_matrix= cosine_similarity(
        vectors
    )

    for i in range(len(questions)):
        for j in range(i + 1, len(questions)):
            similarity= similarity_matrix[i][j]

            if similarity >= DUPLICATE_THRESHOLD:
                report["valid"] = False
                report["errors"].append(
                    f"Question {question_numbers[i]} and Question {question_numbers[j]} appear to be duplicates ({similarity:.2%})."
                )

    return report