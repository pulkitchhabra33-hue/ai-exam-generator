def build_teacher_summary(
        acceptance_report
):
    quality= acceptance_report["quality_score"]
    confidence= acceptance_report["confidence"]
    accepted= acceptance_report["accepted"]

    if quality >= 90:
        stars= "★★★★★"
        quality_label= "Excellent"

    elif quality >= 80:
        stars = "★★★★☆"
        quality_label = "Very Good"

    elif quality >= 70:
        stars = "★★★☆☆"
        quality_label = "Good"

    elif quality >= 60:
        stars = "★★☆☆☆"
        quality_label = "Average"

    else:
        stars = "★☆☆☆☆"
        quality_label = "Poor"

    
    if accepted:
        status= "Ready for download"

    else:
        status= "Needs Improvement"

    
    summary= {
        "rating": stars,
        "quality_level": quality_label,
        "status": status,
        "quality_score": quality,
        "confidence": confidence
    }

    if "reasons" in acceptance_report:
        summary["remarks"] = acceptance_report["reasons"]

    return summary