from pydantic import BaseModel, Field


class Constraint(BaseModel):
    variables: list[str] = Field(description="The names of the variables in the constraint.")
    constraint: str = Field(description="The constraint in string format.")

class Constraints(BaseModel):
    variables: list[str] = Field(description="The names of the variables in the constraint.")
    constraint: list[str] = Field(description="The constraints in string format.")

class SingleVariableExamples(BaseModel):
    examples: list[str] = Field(description="The strings satisfying the constraint.")

class MultiVariableExamples(BaseModel):
    examples: list[dict[str, str]] = Field(description="The list of examples satisfying the constraint. Each examples is a map of string values mapped to their variable names.")

class Judgement(BaseModel):
    evaluator_expression_is_correct: bool = Field(description="Whether the evaluator expression is correct.")
    example_strings_are_correct: bool = Field(description="Whether the example strings are all correct.")