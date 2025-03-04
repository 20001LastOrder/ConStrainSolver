from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

from llm_string.constraint_generator.core.python.prompt import get_template, get_functions, CallableExtension

from llm_string.logging.logging_overrides import getLogger

logger = getLogger()


class BatchPythonGeneratorAgent:
    def __init__(self, model_name='gpt-4o-mini', temperature=0.5):
        if model_name in ["gpt-4o-mini", "gpt-4o"]:
            self.model = ChatOpenAI(model_name=model_name, temperature=temperature)
        elif model_name in ["deepseek-chat", "deepseek-reasoner"]:
            self.model = ChatDeepSeek(model_name=model_name, temperature=temperature)


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
            logger.debug("Attempt {0} invoking model with prompt: {1}", i + 1, prompt)
            try:
                response = self.model.invoke(prompt)

                logger.debug("Received response from model: {0}", response.content)

                return get_functions(response.content)
            except Exception as e:
                logger.error("Error invoking model: {0}", e)

        logger.error("Failed to invoke model after {0} retries", max_retries_per_attempt)
        return [None] * len(constraint_text)
