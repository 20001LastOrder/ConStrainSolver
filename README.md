# ConStrainSolver

## Run LLM Experiments
```bash
python -m scripts.run_llm --approach={llm,smt} --file_path=<path_to_the_constraint_file> --output_path=<path_to_save_results> --llm=<llm_name> [--use_variable_name] --smt_solver={z3}
```

By default, variable names in the prompt sent ot the LLM are replaced with a generic name "x" to avoid any bias introduced by the variable name. If you want to use the variable name in the prompt, you can set the flag `--use_variable_name`.


* e.g. to run an LLM:
```bash
python -m scripts.run_llm --approach llm --file_path=constraint_files/constraints.csv --output_path results/llms --llm gpt-4o-mini
```

* For example, to run an SMT solver:
```bash
python -m scripts.run_llm --approach smt --file_path=constraint_files/constraints.csv --output_path results/smt --smt_solver=z3
```