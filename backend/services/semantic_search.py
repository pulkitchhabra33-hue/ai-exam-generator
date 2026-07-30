import json
from pathlib import Path
from backend.core.ai_client import client
import math

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

def semantic_search(query, repository, top_k= 5):
    query_embedding= generate_embedding(query)

    results= []

    for question in repository["questions"]:
        embedding= generate_embedding(question["question"])

        similarity= cosine_similarity(query_embedding, embedding)

        if similarity >= 0.30:
            results.append((similarity, question))

        results.sort(reverse= True, 
            key= lambda x:x[0]
        )

    return results[:top_k]