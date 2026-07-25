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
{data.get("school_name", "")}

Exam:
{data.get("exam_name", "")}

Class:
{data.get("class_name", "")}

Subject:
{data.get("subject", "")}

Topics:
{data.get("topics", "")}

Difficulty:
{data.get("difficulty", "")}

Total Marks:
{data.get("total_marks", "")}

Section Distribution:
{section_data}

Instructions:
{instructions}

{reference_paper}
"""