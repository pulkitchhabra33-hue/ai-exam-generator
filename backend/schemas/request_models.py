from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionGroupRequest(BaseModel):
    question_type: str
    question_count: int = Field(gt=0)
    marks_per_question: int = Field(gt=0)
    marks: int = Field(gt=0)
    
class SectionRequest(BaseModel):
    section_name: str
    marks: int = Field(gt=0)
    question_count: int = Field(gt=0)
    question_groups: List[QuestionGroupRequest]

class TeacherRequest(BaseModel):

    exam_type: str = "none"
    subject: str
    class_name: str
    total_marks: int = Field(gt=0)

    school_name: Optional[str] = ""
    exam_name: Optional[str] = ""
    time_limit: Optional[str] = ""
    instructions: Optional[str] = ""

    sections: List[SectionRequest]

    include_answers: bool = False
    include_solutions: bool = False