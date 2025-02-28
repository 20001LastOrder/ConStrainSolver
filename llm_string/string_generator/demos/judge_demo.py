from llm_string.logging.logging_overrides import getLogger, addConsoleToLogger
from llm_string.models import Constraint
from llm_string.string_generator.core.judge_agent import JudgeAgent

getLogger()

addConsoleToLogger()

constraint_nl = "The name shall only contain letters a-z, letters A-Z and space characters."
constraint_smt = "(str.in.re name (re.* (re.union (re.range \"a\" \"z\") (re.range \"A\" \"Z\") (str.to.re \" \"))))"

constraint = Constraint(variables=["name"], constraint=constraint_smt)

examples = [{"name": "John_Doe"}, {"name": "Jane_Doe"}, {"name": "John_Smith"}]

judge = JudgeAgent(constraint_type="smt-lib2")

judgement = judge.judge(nl_constraint=constraint_nl, constraint_c=constraint, example_strings=examples)

print(judgement)

