# llm-string-constraints

Artifacts for the paper *"LLM-based Satisfiability Checking of String Requirements by Consistent Data and Checker Generation"*

## Artifact Summary
This repository contains code to run the LLM-based string constraint generation from natural language requirements and generating string values using natural language constraints. It also contains the dataset used in the paper, which is a collection of string constraints and their corresponding checkers in Python and SMT-Lib format. Finally, the scripts to run the constraint generation and string generation used in the paper as well as notebooks to reproduce tables / figures from the paper are provided. 

The artifact can also be customized in the following ways using configuration through [Hydra](https://hydra.cc/docs/intro/):
* Use different local or remote LLMs for the generation of constraints and strings
* Use different validation approaches of the generated strings
* Use different SMT solvers for the validation of the generated strings


## Artifact Location:
The repository is available at: TODO

## Artifact Contents:
The repository contains the following modules:
* `llm_string/constraint_generator`: Contains the code to generate string constraints from natural language requirements using LLMs (For details, see [llm_string/constraint_generator/README.md](llm_string/constraint_generator/README.md)).
* The rest of the `llm_string` folder contains the code to generate string values from the generated constraints using LLMs, including:
    * `llm_string/prompts`: Contains the prompts used for generating string values from constraints.
    * `llm_string/string_solvers`: Contains various solvers for generating string values using LLMs, including validation and feedback. It also contains formal solvers to generate string values using the SMT-Lib format.
    * `llm_string/base.py`: Contains the base classes for the generation results
    * `llm_string/constraints.py`: Contains code to process and store string and formal constraints
    * `llm_string/string_validator.py`: Contains code to validate the generated string values against the constraints using Python or SMT-Lib during the generation process.
    * `string_solvers/structs.py`: Contains the data structures used for the string generation process, including the constraint problem, feedback and solutions.
    * `utils.py`: Contains utility functions for the string generation process.
* `results`: Contains string generation results of the experiments in the paper
* `scripts`: Contains scripts to run the constraint generation and string generation experiments.
* `measurements`: Contains Jupyter notebooks to reproduce the tables and figures in the paper for each RQ.
* `requirements.txt`: Contains the Python dependencies required to run the code in this repository.

## Installation
> Note: All the following commands assumes that you are in the project root directory.

### Install Python
To run the code in this repository, you need to install Python. We recommend using a virtual environment such as [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/en/latest/).

> The code in this repository has been developed with Python 3.12. Earlier or later versions may also work, but are not guaranteed.

Create the virtual environment:
```bash
# For venv
python -m venv constrainsolver

# For conda
conda create -n constrainsolver python=3.12
```

Activate the virtual environment:
```bash
# For venv
source constrainsolver/bin/activate
# For conda
conda activate constrainsolver
```

### Install Dependencies
Install the dependencies using pip:
```bash
pip install -r requirements.txt
```

### Install solvers
Note that the Z3 Solvers are installed automatically when installing dependencies, but you will need to manually install the CVC5 solver:

1. Download the appropriate binary for your platform from the [CVC5 GitHub releases](https://github.com/cvc5/cvc5/releases/). This repository was developed with the `cvc5-Win64-x86_64-static.zip` package.
2. Extract the contents of the zip file into the `solvers` directory at the root of this repository.
3. If necessary, update the path to the CVC5 executable in [llm_string/string_solvers/formal_solvers.py](llm_string/string_solvers/formal_solvers.py#L52).

### LLMs
The code in this repository uses the [LangChain](https://python.langchain.com/docs/) library to interact with LLMs. Specifically, it uses APIs from the following platforms:
* [OpenAI](https://openai.com/): For gpr-4o-mini and gpt-4o
* [DeepSeek](https://deepseek.com/): For DeepSeek v3
* [Together](https://together.xyz/): For Llama3.1-8b

Then, you will need to set the corresponding environment variables for the LLMs:
```bash
export OPENAI_API_KEY=<your_openai_api_key>
export DEEPSEEK_API_KEY=<your_deepseek_api_key>
export TOGETHER_API_KEY=<your_together_api_key>
```

## Run the Experiments

### Run LLM Checker Generation

See [llm_string/constraint_generator/README.md](llm_string/constraint_generator/README.md).

### Run LLM String Generation
See [llm_string/README.md](llm_string/README.md).

### Run Measurements (Tables and Figures in the Paper)
See [measurements/README.md](measurements/README.md).

## Authors and Citations
Please cite the following paper if use found this repository useful:
```bibtex
@inproceedings{chen2025llm,
  author = {Boqi Chen and Aren A. Babikian and Shuzhao Feng and D{\'{a}}niel Varr{\'{o}} and Gunter Mussbacher},
  title  = {{LLM}-based Requirements Verification Through Consistent Text Data and Checker Generation},
  booktitle = {33rd {IEEE} International Requirements Engineering Conference, {RE} 2025, Valencia, Spain, September 1-5, 2025},
  publisher = {{IEEE}},
  year   = {2025}
}
```

## License
The code and data in this repository are licensed under the [MIT License](./LICENSE). 
