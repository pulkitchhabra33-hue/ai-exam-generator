from backend.core.ai_client import client
import math
from backend.services.retrieval_ranker import calculate_rank_score

def generate_embedding(text):
    response= client.embeddings.create(
        model= "text-embedding-3-small",
        input= text
    )

    return response.data[0].embedding

def cosine_similarity(vector1, vector2):
    dot= sum(a*b for a, b in zip(vector1, vector2))

    magnitude1= math.sqrt(sum(a*a for a in vector1))
    magnitude2= math.sqrt(sum(b*b for b in vector2))

    return dot/ (magnitude1 * magnitude2)

def semantic_search(query, 
                repository,
                teacher_requirements= None,
                top_k= 5):
    
    query_embedding= generate_embedding(query)

    results= []

    cached = 0
    generated = 0

    for question in repository["questions"]:
        question_embedding= question.get("embedding")

        if question_embedding is None:
            generated += 1

            question_embedding= generate_embedding(
                question["question"]
            )

            question["embedding"] = question_embedding

        else:
            cached += 1

        similarity= cosine_similarity(
            query_embedding,
            question_embedding
        )

        if teacher_requirements:
            score= calculate_rank_score(
                similarity,
                question,
                teacher_requirements
            )

        else:
            score= similarity

        results.append((score, question))

    results.sort(reverse= True, 
        key= lambda x:x[0]
    )

    print()
    print(f"Cached Embeddings : {cached}")
    print(f"Generated : {generated}")
    print()
    
    return results[:top_k]