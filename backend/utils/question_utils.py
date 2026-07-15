def build_question_id(
    section,
    index
):
    return f"{section.get('section_name', '?')}-{index}"