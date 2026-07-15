import language_tool_python
from backend.utils.question_utils import build_question_id

tool= language_tool_python.LanguageTool("en-US")

def validate_grammar(
        generated_paper
):
    
    report= {
        "valid": True,
        "errors": []
    }

    for section in generated_paper.get("sections", []):
        for index, question in enumerate(section.get("questions", []), start=1):
            text= question.get(
                "question_text", ""
            ).strip()

            if not text:
                continue
        
            matches= tool.check(text)

            important= [
                match
                for match in matches
                if match.rule_issue_type.lower() != "style"
            ]

            issues= []
            for match in important:
                if match.replacements:
                    issues.append(
                        f"{match.message} Suggestions: {', '.join(match.replacements[:3])}"
                    )

                else:
                    issues.append(match.message)

            question_id = build_question_id(
                section,
                index
            )

            if important:
                report["valid"]= False
                report["errors"].append(
                    f"Question {question_id}: " + "; ".join(issues)
                )

    return report