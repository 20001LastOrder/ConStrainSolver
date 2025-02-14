from pydantic import BaseModel, Field


class Result(BaseModel):
    value: str = Field(description="The string value that satisfies the constraints.")
