# llm-string-constraints

## Run LLM Experiments
```bash
python -m scripts.run_generation --approach={llm,smt} --file_path=<path_to_the_constraint_file> --output_path=<path_to_save_results> --llm=<llm_name> [--use_variable_name] --smt_solver={z3}
```

By default, variable names in the prompt sent ot the LLM are replaced with a generic name "x" to avoid any bias introduced by the variable name. If you want to use the variable name in the prompt, you can set the flag `--use_variable_name`.

### Suggested workflow

* Run an LLM:
```bash
python -m scripts.run_generation --approach llm --file_path=constraint_files/constraints.csv --output_path results/llms --llm gpt-4o-mini --use_variable_name
```

* Validate the generated LLM outputs
    * Note: this (1) reads the generated .csv file, (2) validates it line by line and (3) generates a new file which is a copy of the .csv file, extended with a validation column checking whetherthe generated strings actually satify the constraints
    * Note that the file it will read to find the llm outputs is computed from the `output_path`, `llm` and `use_variable_name` arguments, s for the `llm` approach.
```bash
python -m scripts.run_generation --approach validate --file_path=constraint_files/constraints.csv --output_path results/llms --llm gpt-4o-mini
```

* Run an SMT solver:
```bash
python -m scripts.run_generation --approach smt --file_path=constraint_files/constraints.csv --output_path results/smt --smt_solver=z3
```
