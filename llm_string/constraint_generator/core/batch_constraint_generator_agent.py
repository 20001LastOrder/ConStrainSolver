from func_timeout import FunctionTimedOut
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from llm_string.constraint_generator.core.history_helper import format_history
from llm_string.string_generator.core.judge_agent import JudgeAgent
from llm_string.string_generator.core.string_generator_agent import StringGeneratorAgent
from llm_string.utils import JSONPydanticOutputParser

from llm_string.constraint_generator.core.constraint_evaluator import ConstraintEvaluator
from llm_string.models import Constraints, Constraint
from llm_string.constraint_generator.core.prompt_template_generator import get_prompt_template

from llm_string.logging.logging_overrides import getLogger

logger = getLogger()


class BatchConstraintGeneratorAgent:
    _naive: bool
    _max_retries_per_step: int
    _number_of_items: int
    _nl_constraints: list[str]
    _evaluator: ConstraintEvaluator
    _string_generator_agent: StringGeneratorAgent
    _judge_agent: JudgeAgent


    def __init__(self, constraint_type: str, model_name='gpt-4o-mini', temperature=0.5):
        parser = JSONPydanticOutputParser(pydantic_object=Constraints)

        prompt_template = get_prompt_template(constraint_type, parser, independent=False)

        if model_name == "gpt-4o-mini" or model_name == "gpt-4o":
            model = ChatOpenAI(model_name=model_name, temperature=temperature)
        elif model_name == "deepseek-chat":
            model = ChatDeepSeek(model_name=model_name, temperature=temperature)
        elif model_name == "llama3.1-8b-instruct-q4_0":
            model = ChatOllama(model=model_name, temperature=temperature)

        self.chain = prompt_template | model | parser
        self.constraint_type = constraint_type
        self.model_name = model_name
        self.temperature = temperature

        self.levels = [self._execute_evaluator_step, self._execute_examples_step, self._execute_judge_step]
        self.min_level = -1
        self.max_level = -1

        self._naive = True
        self._max_retries_per_step = 0
        self._number_of_items = 10
        self._nl_constraints = []
        self._evaluator = None
        self._string_generator_agent = None
        self._judge_agent = None


    def get_evaluator(
            self,
            constraint_text: list[str],
            use_examples=False,
            use_judge=False,
            max_steps=1,
            max_retries_per_attempt=0,
            naive=True
    ) -> tuple[ConstraintEvaluator, int, int]:
        self._nl_constraints = constraint_text
        self._max_retries_per_step = max_retries_per_attempt
        self._naive = naive

        self.min_level = 0
        self.max_level = 1  # generate evaluator -> done

        if use_examples:
            self.max_level = 2  # generate evaluator -> test with examples -> done

            if use_judge:
                raise NotImplementedError("Judgement is not implemented yet.")
                self.max_level = 3  # generate evaluator -> test with examples -> judgement -> done

        return self._execute_steps(max_steps)


    def setup_steps(
            self,
            constraint_text: list[str],
            use_examples=False,
            use_judge=False,
            max_retries_per_attempt=0,
            naive=True
    ):

        self._nl_constraints = constraint_text
        self._max_retries_per_step = max_retries_per_attempt
        self._naive = naive

        self.min_level = 0
        self.max_level = 1  # generate evaluator -> done

        if use_examples:
            self.max_level = 2  # generate evaluator -> test with examples -> done

            if use_judge:
                raise NotImplementedError("Judgement is not implemented yet.")
                self.max_level = 3  # generate evaluator -> test with examples -> judgement -> done


    def _execute_steps(self, max_steps: int) -> tuple[ConstraintEvaluator, int, int]:
        current_level = 0
        current_steps = 0

        while current_steps < max_steps and current_level < self.max_level:
            step_result = self.levels[current_level]()

            current_level = max(min(current_level + step_result, self.max_level), self.min_level)
            current_steps += 1

        return self._evaluator, current_level, current_steps


    def step(self, current_level: int) -> tuple[ConstraintEvaluator, int]:
        step_result = self.levels[current_level]()

        current_level = max(min(current_level + step_result, self.max_level), self.min_level)

        return self._evaluator, current_level


    def _execute_evaluator_step(self) -> int:
        if self._naive:
            return self._execute_evaluator_step_naive()
        else:
            return self._execute_evaluator_step_advanced()


    def _execute_evaluator_step_naive(self) -> int:
        evaluator = ConstraintEvaluator()
        attempt = 0
        history = []

        while attempt <= self._max_retries_per_step:
            logger.info("Attempt {0}: sending constraint to the LLM: {1}", attempt + 1, str(self._nl_constraints))

            try:
                constraints = self._invoke_chain(self._nl_constraints, history)

                if len(constraints.constraint) != len(self._nl_constraints):
                    raise ValueError(f"Constraint lengths do not match. Expected: {len(self._nl_constraints)}, got: {len(constraints.constraint)}")
            except Exception as e:
                logger.error("Error invoking chain: {0}", str(e))
                attempt += 1
                continue

            logger.info("Received constraints from the LLM: {0}", str(constraints))

            try:
                evaluator, error_list = ConstraintEvaluator.create_evaluator_with_multiple_constraints(self.constraint_type, constraints)

                if len(error_list) == 0:
                    logger.info("Successfully created evaluator. Returning evaluator.")
                    self._evaluator = evaluator

                    return 1

                raise ValueError(f"Error creating evaluator.", _parse_error_list(error_list, constraints.constraint))
            except FunctionTimedOut:
                logger.error("Timeout creating evaluator.")
                attempt += 1
                continue
            except Exception as e:
                logger.error("Error creating evaluator for constraint {0}: {1}", constraints, str(e))
                history.extend([(Constraint(variables=constraints.variables, constraint=c), ex) for c, ex in (e.args[1] if len(e.args) > 1 else [])])
                attempt += 1

        logger.error("Failed to create evaluator after {0} attempts. See log for details.", self._max_retries_per_step + 1)
        self._evaluator = evaluator

        return -1


    def _execute_evaluator_step_advanced(self) -> int:
        evaluator = ConstraintEvaluator()
        constraint_generated = Constraints(variables=[], constraint=[])
        constraint_generated.constraint = [None for _ in self._nl_constraints]

        attempt = 0
        history = []

        while attempt <= self._max_retries_per_step:
            nl_constraint_to_generate = [nl_constraint for i, nl_constraint in enumerate(self._nl_constraints) if constraint_generated.constraint[i] is None]

            logger.info("Attempt {0}: sending constraint to the LLM: {1}", attempt + 1, str(nl_constraint_to_generate))

            try:
                constraints = self._invoke_chain(nl_constraint_to_generate, history)

                constraints = _postprocess_constraints(constraints)

                constraint_generated = _merge_constraints(constraint_generated, constraints)
            except Exception as e:
                logger.error("Error invoking chain: {0}", str(e))
                attempt += 1
                continue

            logger.info("Received constraints from the LLM: {0}", str(constraints))

            try:
                evaluator, error_list = ConstraintEvaluator.create_evaluator_with_multiple_constraints(self.constraint_type, constraint_generated)

                if len(error_list) == 0:
                    logger.info("Successfully created evaluator. Returning evaluator.")
                    self._evaluator = evaluator

                    return 1

                if -1 in [err[0] for err in error_list]:
                    # constraint is unsatisfiable, and we can't pinpoint which constraint is correct and which is not.
                    parsed_error_list = _parse_error_list(error_list, constraint_generated.constraint)
                    constraint_generated.constraint = [None for _ in self._nl_constraints]
                    raise ValueError(f"Error creating evaluator.", parsed_error_list)

                parsed_error_list = _parse_error_list(error_list, constraint_generated.constraint)

                for i, nl_constraint in enumerate(self._nl_constraints):
                    if i in [err[0] for err in error_list]:
                        constraint_generated.constraint[i] = None

                raise ValueError(f"Error creating evaluator.", parsed_error_list)

            except Exception as e:
                logger.error(str(e))
                history.extend([(Constraint(variables=constraint_generated.variables, constraint=c), ex) for c, ex in e.args[1]])
                attempt += 1

        logger.error("Failed to create evaluator after {0} attempts. See log for details.", self._max_retries_per_step + 1)
        self._evaluator = evaluator

        return -1


    def _execute_examples_step(self) -> int:
        self._failed_examples = []

        if self._string_generator_agent is None:
            self._string_generator_agent = StringGeneratorAgent(self.model_name, self.temperature)

        try:
            example_strings = self._string_generator_agent.generate_strings_with_retries(
                self._nl_constraints,
                variables=self._evaluator.constraint.variables,
                number_of_items=self._number_of_items,
                max_retries=self._max_retries_per_step
            )
        except Exception as e:
            logger.error("Error generating example strings: {0}", str(e))
            return 1

        failed_examples = []

        for example in example_strings:
            if not self._evaluator.safe_evaluate(*example):
                failed_examples.append(example)

        if len(failed_examples) == 0:
            logger.info("Evaluation of all examples succeeded.")

            return 1

        logger.error("Evaluation of examples failed. Failed examples: {0}", failed_examples)
        self._failed_examples = failed_examples

        return -1


    def _execute_judge_step(self) -> int:
        pass


    def _invoke_chain(self, constraint_text: list[str], history: list[tuple[Constraints, Exception]]) -> Constraints:
        history_text = format_history(history)
        logger.debug("Full prompt: {0}", self.chain.steps[0].invoke({"constraint": str(constraint_text), "history": history_text}))

        constraint = self.chain.invoke({"constraint": str(constraint_text), "history": history_text})

        # a common issue is that the LLM would add a punctuation mark at the end of the last constraint,
        # which is an easy fix, so we can fix it here.
        for i in range(len(constraint.constraint)):
            if constraint.constraint[i][-1] in [";", ",", ".", "\n"]:
                constraint.constraint[i] = constraint.constraint[i][:-1]

        return constraint


def _merge_constraints(old_constraints: Constraints, new_constraints: Constraints):
    if len(old_constraints.variables) > 0 and old_constraints.variables != new_constraints.variables:
        raise ValueError("Variables do not match.", old_constraints.variables, new_constraints.variables)

    expected = sum(1 for constraint in old_constraints.constraint if constraint is None)
    got = len(new_constraints.constraint)
    if expected != got:
        raise ValueError(f"Constraints lengths do not match. Expected: {expected}, got: {got}")

    old_constraints.variables = new_constraints.variables

    new_constraints_ptr = 0

    for i, old_constraint in enumerate(old_constraints.constraint):
        if old_constraint is None:
            old_constraints.constraint[i] = new_constraints.constraint[new_constraints_ptr]
            new_constraints_ptr += 1

    return old_constraints


def _parse_error_list(error_list: list[tuple[int, Exception]], constraint: list[str]) -> list[tuple[str, Exception]]:
    return [(constraint[i] if i >= 0 else "constraint satisfiability", error) for i, error in error_list]


def _postprocess_constraints(constraints: Constraints) -> Constraints:
    for i in range(len(constraints.constraint)):
        # a common issue is that the LLM would append a punctuation mark to the end of the constraint
        if not constraints.constraint[i].endswith(")"):
            constraints.constraint[i] = constraints.constraint[i][:-1]

        # another common issue is to already wrap the answer in an assert statement
        if constraints.constraint[i].startswith("(assert "):
            constraints.constraint[i] = constraints.constraint[i][8:-1]
        
        constraints.constraint[i] = constraints.constraint[i].replace("str.to.re", "str.to_re")
        constraints.constraint[i] = constraints.constraint[i].replace("str.in.re", "str.in_re")
        constraints.constraint[i] = constraints.constraint[i].replace("str.to.int", "str.to_int")
        constraints.constraint[i] = constraints.constraint[i].replace("re.complement", "re.comp")

    return constraints

def postprocess_constraint(constraint: str) -> str:
    if not isinstance(constraint, str):
        return constraint

    if not constraint.endswith(")"):
        constraint = constraint[:-1]

    if constraint.startswith("(assert "):
        constraint = constraint[8:-1]

    constraint = constraint.replace("str.to.re", "str.to_re")
    constraint = constraint.replace("str.in.re", "str.in_re")
    constraint = constraint.replace("str.to.int", "str.to_int")
    constraint = constraint.replace("re.complement", "re.comp")

    return constraint
