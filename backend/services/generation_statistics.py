from datetime import datetime

def build_generation_statistics(
        report,
        quality_score,
        confidence
):
    return {
        "generated_at": datetime.now().isoformat(),
        "attempts": report["attempts"],
        "best_attempt": report["best_attempt"],
        "valid": report["valid"],
        "remaining_errors": report["remaining_errors"],
        "quality_score": quality_score,
        "confidence": confidence
    }