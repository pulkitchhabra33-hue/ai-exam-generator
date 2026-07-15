MIN_QUALITY_SCORE= 80
MIN_CONFIDENCE= 80
MAX_ALLOWED_ERRORS= 3

def should_accept(statistics):
    quality= statistics["quality_score"]
    confidence= int(statistics["confidence"].replace("%", ""))
    errors= statistics["remaining_errors"]

    accepted= (
        quality >= MIN_QUALITY_SCORE
        and
        confidence >= MIN_CONFIDENCE
        and
        errors <= MAX_ALLOWED_ERRORS
    )

    reasons= []

    if quality < MIN_QUALITY_SCORE:
        reasons.append(
            "Quality score below threshold."
        )

    if confidence < MIN_CONFIDENCE:
        reasons.append(
            "Confidence below threshold."
        )

    if errors > MAX_ALLOWED_ERRORS:
        reasons.append(
            "Too many validation errors."
        )

    result= {
        "accepted": accepted,
        "quality_score": quality,
        "confidence": confidence,
        "remaining_errors": errors,
    }

    if reasons:
        result["reasons"]= reasons

    return result