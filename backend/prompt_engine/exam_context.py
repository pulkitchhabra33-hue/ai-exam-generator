def get_exam_context(
        data,
        exam_type,
        section_data,
        instructions,
        reference_paper
):
    return f"""
--------------------------------------------------
EXAM DETAILS
--------------------------------------------------

Exam Type:
{exam_type}

School:
{data.school_name}

Exam:
{data.exam_name}

Class:
{data.class_name}

Subject:
{data.subject}

Topics:
{data.topics}

Difficulty:
{data.difficulty}

Total Marks:
{data.total_marks}

Section Distribution:
{section_data}

Instructions:
{instructions}

{reference_paper}
"""