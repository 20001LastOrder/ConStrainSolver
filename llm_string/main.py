from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from llm_string.utils import REPydanticOutputParser

PROMPT_TEXT = """First, explain the meaning of each constraint. Then find a string value for {name} that satisfy ALL following constraints:
{constraints}
The value should be as realistic for {name} as possible.

The output should follow the following format, if not possible, assign the value "UNSAT":
{output_format}

Result:
"""

# constraints = """
# imageURL.substring(0, 6) = "http://" or imageURL.substring(0, 7) = "https://"
# imageURL <> ""
# imageURL <> null
# """

# name = "imageURL"

constraints = """
    password.length() <= 3
    password.contains("!") or password.contains("#") or password.contains("$")
    there exists a character c in password such that Character.isUpperCase(c) = true
    there exists a character c in password such that Character.isLowerCase(c) = true
"""

name = "password"


class Result(BaseModel):
    value: str = Field(description="The string value that satisfies the constraints.")


def main():
    llm = ChatOpenAI(model="gpt-4o-mini")

    # TODO: This parser does not work with COT, need to create a new parser
    parser = REPydanticOutputParser(pydantic_object=Result)

    print(parser.get_format_instructions())
    prompt_template = PromptTemplate(
        template=PROMPT_TEXT,
        input_variables=["name", "constraints"],
        partial_variables={"output_format": parser.get_format_instructions()},
    )

    chain = prompt_template | llm

    result = chain.invoke(
        input={
            "name": name,
            "constraints": constraints,
        }
    )

    print(result.content)
    print(parser.parse(result.content))


if __name__ == "__main__":
    main()
