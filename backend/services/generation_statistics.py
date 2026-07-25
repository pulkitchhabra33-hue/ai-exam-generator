from datetime import datetime

def build_generation_statistics(
        validation_report,
        generation_statistics,
        quality_score,
        confidence
):
    return {
        "generated_at": datetime.now().isoformat(),
        "attempts": generation_statistics["attempts"],
        "best_attempt": generation_statistics["best_attempt"],
        "valid": validation_report["valid"],
        "remaining_errors": generation_statistics["remaining_errors"],
        "quality_score": quality_score,
        "confidence": confidence
    }