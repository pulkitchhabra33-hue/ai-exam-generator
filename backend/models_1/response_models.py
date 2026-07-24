from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TeacherSummary(BaseModel):
    rating: str
    quality_level: str
    status: str


class Acceptance(BaseModel):
    accepted: bool
    reason: Optional[List[str]] = None


class Statistics(BaseModel):
    attempts: int
    best_attempt: int
    valid: bool
    remaining_errors: int
    quality_score: int
    confidence: int
    generation_time: float
    validation_time: float
    pipeline_time: float


class FinalResult(BaseModel):
    paper: Dict[str, Any]
    statistics: Statistics
    acceptance: Acceptance
    teacher_summary: TeacherSummary


class GenerationResponse(BaseModel):
    success: bool
    result: Optional[FinalResult] = None
    error: Optional[str] = None