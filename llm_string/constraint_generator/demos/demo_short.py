from llm_string.constraint_generator import get_constraint_evaluator

evaluator = get_constraint_evaluator(
    ["The email shall contain no space characters.", "The email shall contain a @ character."],
    generator_type="batch",
    constraint_type="smt-lib2",
)

if evaluator is not None:
    print(evaluator.safe_evaluate("john doe@gmail.com")) # False




