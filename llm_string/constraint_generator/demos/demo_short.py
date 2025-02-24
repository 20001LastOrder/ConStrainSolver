from llm_string.constraint_generator import get_constraint_evaluator, get_constraint

evaluator = get_constraint_evaluator(
    ["The email shall contain no space characters.", "The email shall contain a @ character."],
    generator_type="batch",
    constraint_type="smt-lib2",
    max_retries_per_attempt=1,
    max_steps=5,
    use_examples=True,
    verbose=True
)

if evaluator is not None:
    print(evaluator.safe_evaluate("john doe@gmail.com"))

    print(evaluator.constraint.constraint)

# alternatively, from llm_string.constraint_generator import get_constraint,
# and call the function with the same parameters as get_constraint_evaluator
