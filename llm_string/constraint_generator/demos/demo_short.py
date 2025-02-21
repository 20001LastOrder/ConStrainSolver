from llm_string.constraint_generator import get_constraint_evaluator

evaluator = get_constraint_evaluator(
    "The email shall contain no space characters.",
    constraint_type="smt-lib2"
)

print(evaluator.safe_evaluate("john doe@gmail.com"))
