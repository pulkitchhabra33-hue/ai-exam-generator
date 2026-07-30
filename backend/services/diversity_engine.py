import random

def diversify_results(
    ranked_results,
    top_k= 10,
    fixed_top= 3,
    candidate_pool= 20,
    similarity_threshold= 0.3
):
    filtered= [
        result
        for result in ranked_results
        if result[0] >= similarity_threshold
    ]

    guaranteed= filtered[:fixed_top]

    remaining= filtered[fixed_top: candidate_pool]

    random.shuffle(remaining)

    needed= max(
        0,
        top_k - len(guaranteed)
    )

    return guaranteed + remaining[:needed]