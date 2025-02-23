from llm_string.constraint_generator import get_constraint_evaluator

evaluator = get_constraint_evaluator(
    "The email shall contain no space characters.",
    constraint_type="smt-lib2"
)

if evaluator is not None:
    print(evaluator.safe_evaluate("john doe@gmail.com"))

print(evaluator.constraint.constraint)
# alternatively, from llm_string.constraint_generator import get_constraint,
# and call the function with the same parameters as get_constraint_evaluator
