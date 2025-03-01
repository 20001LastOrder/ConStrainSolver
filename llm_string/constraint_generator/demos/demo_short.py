# from llm_string.constraint_generator import get_constraint_evaluator
#
# evaluator = get_constraint_evaluator(
#     ["The email shall contain no space characters.", "The email shall contain a @ character."],
#     generator_type="batch",
#     constraint_type="smt-lib2",
# )
#
# if evaluator is not None:
#     print(evaluator.safe_evaluate("john doe@gmail.com")) # False
from llm_string.constraint_generator.core.batch_constraint_generator_agent import BatchConstraintGeneratorAgent

agent = BatchConstraintGeneratorAgent(constraint_type="smt-lib2")

agent.setup_steps(
    [
        "The name shall only contain letters a-z, letters A-Z and space characters.",
        "The name shall contain at least one space character.",
        "The name shall not end with a space character.",
        "The name shall not  start with a space character.",
        # "The first character in the name shall be capitalized.",
        # "Any character in the name following a space character shall be capitalized."
    ],
    max_retries_per_attempt=2,
    use_examples=True,
    naive=False,
)

current_level = 0

print("Initial level:", current_level)
print("Initial constraint:", None)

for i in range(5):
    print("Step ", i + 1)
    evaluator, current_level = agent.step(current_level)

    print("New level:", current_level)
    print("New constraint:", evaluator.constraint.constraint)

    if current_level >= 2:
        break

print("Final level:", current_level)
print("Final constraint:", evaluator.constraint.constraint)




