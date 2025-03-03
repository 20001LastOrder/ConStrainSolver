from llm_string.constraint_generator.core.python import BatchPythonGeneratorAgent

agent = BatchPythonGeneratorAgent(model_name='deepseek-chat')

evaluator = agent.get_evaluator(["The string must contain the word 'hello'.", "The string must contain the word 'world'."])

print([e.source for e in evaluator])

print(evaluator[0]("hello world"))
