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
Or, if you use conda:
```bash
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

<TODO: Add instructions for installing CVC5>

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

## Run LLM Checker Generation

See [llm_string/constraint_generator/README.md](llm_string/constraint_generator/README.md).

## Run LLM String Generation
### Run single LLM calls
* Available options:
    * <llm>: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b

```bash
python -m scripts.run_generation string_solver=llm_solver constraint_store=re_full output_folder="outputs/llm/<llm>" string_solver/llm=<llm>
```

### Run LLM with validation (+V)
* Available options:
    * <llm>: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b
    * <validator>: ground_truth_python, ground_truth_smt, hybrid (special case)

Run python or smt
```bash
python -m scripts.run_generation string_solver=llm_solver_with_validation constraint_store=re_full string_solver/validator=<validator> string_solver/llm=<llm> output_folder="outputs/${string_solver.name}/<validator>/<llm>"
```

Run the hybrid approach
```bash
python -m scripts.run_generation string_solver=llm_solver_with_validation constraint_store=re_full string_solver/validator=<validator> string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/${string_solver.name}/<validator>/<llm>"
```

### Run LLM with feedback (+VF)
* Available options:
    * <llm>: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b
    * <validator>: ground_truth_python, ground_truth_smt, hybrid (special case)

Run python or smt
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=<validator> string_solver/llm=<llm> output_folder="outputs/${string_solver.name}/<validator>/<llm>"
```

Run the hybrid approach
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/${string_solver.name}/hybrid/<llm>"
```

### Run LLM with explanation (+VFE)
* Available options:
    * <llm>: gpt-4o-mini_v, gpt-4o_v, deepseek-v3_v, llama3.1-8b_v
    * Each validator takes slightly different arguments

Run python validator
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_python string_solver/llm=<llm> output_folder="outputs/llm_solver_with_explanation/python/<llm>" +string_solver.with_explanation=True
```

Run smt validator
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=<llm> output_folder="outputs/llm_solver_with_explanation/smt/<llm>" +string_solver.with_explanation=True +string_solver/validator.produce_failed_constraints=True
```

Run hybrid validator
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/llm_solver_with_explanation/hybrid/<llm>" +string_solver.with_explanation=True
```


## Generation with generated constraints
Run hybrid validator with explanation
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback string_solver/validator=ground_truth_smt string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/generated_constraints/gpt-4o-mini/vfe/<llm>" +string_solver.with_explanation=True constraint_store=re_generated.yaml
```




* Validate the generated LLM outputs
    * Note: this (1) reads the generated .csv file, (2) validates it line by line and (3) generates a new file which is a copy of the .csv file, extended with a validation column checking whether the generated strings actually satisfy the constraints
    * Note that the file it will read to find the llm outputs is computed from the `output_path`, `llm` and `use_variable_name` arguments, s for the `llm` approach.
```bash
python -m scripts.run_evaluation input_path=outputs/llm_with_validation/2025-02-28_15-52-28/gpt-4o-mini.csv
```

* Run a SMT solver:
```bash
python -m scripts.run_generation --approach smt --file_path=constraint_files/constraints.csv --output_path results/smt --smt_solver=z3
```


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

# License
The code and data in this repository are licensed under the [MIT License](./LICENSE). 
