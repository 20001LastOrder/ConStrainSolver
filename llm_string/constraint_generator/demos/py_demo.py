from llm_string.constraint_generator.core.python import BatchPythonGeneratorAgent

agent = BatchPythonGeneratorAgent()

callable_list = agent.get_evaluator(
    constraint_text=["The email shall contain no space characters.", "The email shall contain a @ character."],
)

for call in callable_list:
    print(call.source)
    print(call("John doe@email.com"))