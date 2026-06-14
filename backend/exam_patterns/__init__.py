from backend.exam_patterns.cbse import CBSE_PROMPT
from backend.exam_patterns.icse import ICSE_PROMPT
from backend.exam_patterns.jee import JEE_PROMPT
from backend.exam_patterns.neet import NEET_PROMPT
from backend.exam_patterns.ssc import SSC_PROMPT
from backend.exam_patterns.default import DEFAULT_PROMPT
from backend.exam_patterns.blueprints import get_blueprint

def get_exam_prompt(exam_type):

    if not exam_type:
        return DEFAULT_PROMPT
    
    exam_type= exam_type.lower()

    if "cbse" in exam_type:
        return CBSE_PROMPT
    
    elif "icse" in exam_type:
        return ICSE_PROMPT
    
    elif "jee" in exam_type:
        return JEE_PROMPT
    
    elif "neet" in exam_type:
        return NEET_PROMPT
    
    elif "ssc" in exam_type:
        return SSC_PROMPT
    
    return DEFAULT_PROMPT
