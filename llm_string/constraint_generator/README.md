# Constraint Generator
> Note: All the following commands assumes that you are in the project root directory.

This module is designed to generate constraint checkers for string verification.

Note: you must have corresponding API keys in your environment variables (e.g. OPENAI_API_KEY for GPT models) for the LLM calls to work properly.

## Options

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

## Put Constraints for String Generation
Once you have generated the constraints, you can put them to the corresponding csv files in `constraint_files\generated` folder depending on the LLM used.

Some examples of generated constraints are available in the `constraint_files\generated` folder, which you can use as a reference to run the string generation experiments.

## Show Results from our Experiments

This relies on CSV files from the `llm_string/constraint_generator/evaluations/results/` folder, which are computed by postprocessing the raw results.

```bash
python -m llm_string.constraint_generator.evaluations.show_results
```