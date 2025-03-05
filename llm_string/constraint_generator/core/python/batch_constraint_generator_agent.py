from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether

from llm_string.constraint_generator.core.python.prompt import get_template, get_functions, CallableExtension

from llm_string.logging.logging_overrides import getLogger

logger = getLogger()


class BatchPythonGeneratorAgent:
    def __init__(self, model_name='gpt-4o-mini', temperature=0.5):
        if model_name == "gpt-4o-mini" or model_name == "gpt-4o":
            self.model = ChatOpenAI(model_name=model_name, temperature=temperature)
        elif model_name == "deepseek-chat":
            self.model = ChatDeepSeek(model_name=model_name, temperature=temperature)
        elif model_name == "Meta-Llama-3.1-8B-Instruct-Turbo-128K":
            self.model = ChatTogether(model_name=f"meta-llama/{model_name}", temperature=temperature)


    def get_evaluator(
            self,
            constraint_text: list[str],
            use_examples=False,
            use_judge=False,
            max_retries_per_attempt=0,
    ) -> list[CallableExtension]:
        if use_examples or use_judge:
            raise NotImplementedError()

        prompt = get_template(constraint_text)

        for i in range(max_retries_per_attempt + 1):
            logger.info("constraint={0}, attempt {1} invoking model.", str(constraint_text), i + 1)
            logger.debug("Attempt invoking model with prompt: {0}", prompt)
            try:
                response = self.model.invoke(prompt)

                logger.debug("Received response from model: {0}", response.content)

                functions = get_functions(response.content)

                if len(functions) != len(constraint_text):
                    raise ValueError("Number of functions does not match number of constraints")

                return functions
            except Exception as e:
                logger.error("Error invoking model: {0}", e)

        logger.error("Failed to invoke model after {0} retries", max_retries_per_attempt)
        return [None] * len(constraint_text)
