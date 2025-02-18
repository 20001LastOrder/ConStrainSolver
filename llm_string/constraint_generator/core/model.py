from pydantic import BaseModel, Field


class Constraint(BaseModel):
    variables: list[str] = Field(description="The names of the variables in the constraint.")
    constraint: str = Field(description="The constraint in string format.")