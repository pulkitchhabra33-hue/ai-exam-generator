from backend.validators.grammar_validator import validate_grammar


def main():

    print("=" * 60)
    print("GRAMMAR VALIDATOR TEST")
    print("=" * 60)

    generated_paper = {

        "sections": [

            {
                "name": "Section A",

                "questions": [

                    {
                        "question_text":
                            "Ohm's Law states that voltage are equal to current multiplied by resistance."
                    },

                    {
                        "question_text":
                            "Explain the relationship between voltage, current, and resistance."
                    },

                    {
                        "question_text":
                            "What is the unit of electric current?"
                    }

                ]
            }

        ]
    }

    report = validate_grammar(
        generated_paper
    )

    print("\nValidation Report:")
    print(report)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()