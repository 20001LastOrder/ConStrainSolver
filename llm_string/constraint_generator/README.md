# Constraint Generator

This module is designed to generate constraint checkers for string verification.

Note: you must have corresponding API keys in your environment variables (e.g. OPENAI_API_KEY for GPT models) for the LLM calls to work properly.

## Content

### Core

- `constraint_generator_prompt.txt` and `constraint_generator_history_prompt.txt`: The prompts used to generate Python and SMT checkers.
- `batch_constraint_generator_agent.py`: core logic for generating SMT checkers.
- `python\batch_constraint_generator_agent.py`: core logic for generating Python checkers.

The rest are utility files that are used by the core logic.

### Evaluations

- `evaluations/demo.ipynb`: A Jupyter notebook demonstrating the generation of Python or SMT checkers for given constraints.
- `evaluations/main_py.py`: The main script for running Python checker generation experiments.
- `evaluations/main_smt.py`: The main script for running SMT checker generation experiments.
- `evaluations/postprocessing.py`: A script to postprocess the raw results from each run to summarizing CSV files. Its functions are already integrated into the `main_py.py` and `main_smt.py` scripts, so you don't need to run it separately unless you want to reprocess the results.
- `evaluations/postpostprocessing.py`: A standalone script to take the result of the post processing and generate the final results in a more readable format.
- `evaluations/show_results.py`: A script to display results from our experiments. It relies on the content within the `evaluations/results/` folder.
- `evaluations/results/`: Results from our experiments. You can use the `show_results.py` script to visualize them.
- 

## Run Options

- `generator_mode`: `independent` or `batch`.
- `num_processes`: an integer.
- `max_retries_per_attempt`: an integer.
- `output_folder`: a string. Defaults to `llm_string/constraint_generator/evaluations/results/`
- `model_names`: a list of strings. Available options include:
  - gpt-4o-mini
  - gpt-4o
  - deepseek-chat
  - Meta-Llama-3.1-8B-Instruct-Turbo-128K

## Setup

Always make sure you are in the project root directory before running the commands.

```bash
cd ConstraintSolver
pip install -r requirements.txt
```

## Generate Python Checkers

```bash
python -m llm_string.constraint_generator.evaluations.main_py generator_mode=<generator_mode> num_processes=<num_processes> max_retries_per_attempt=<max_retries_per_attempt> output_folder=<output_folder>  model_names=<model_names> 
```

## Generate SMT Checkers

```bash
python -m llm_string.constraint_generator.evaluations.main_smt generator_mode=<generator_mode> num_processes=<num_processes> max_retries_per_attempt=<max_retries_per_attempt> output_folder=<output_folder>  model_names=<model_names>
```

## Postprocess Generation Results

```bash
python -m llm_string.constraint_generator.evaluations.postpostprocessing
```

Due to limitations in the Z3 solver library, this script may fail when it encounters complex constraints. You can simply rerun the command, and it will skip the failed constraints and continue processing the rest, until all constraints are processed.

## Show Results from our Experiments

This relies on CSV files from the `llm_string/constraint_generator/evaluations/results/` folder, which are computed by postprocessing the raw results.

```bash
python -m llm_string.constraint_generator.evaluations.show_results
```