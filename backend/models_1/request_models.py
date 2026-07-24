from typing import List, Optional
from pydantic import BaseModel, Field

class SectionRequest(BaseModel):
    section_name: str
    marks: int= Field(gt=0)
    question_count: int= Field(gt=0)
    marks_per_question: int= Field(gt=0)

class TeacherRequest(BaseModel):
    exam_type: str
    subject: str
    class_name: str
    total_marks: int= Field(gt=0)
    sections: List[SectionRequest]
    instructions: Optional[str]= ""