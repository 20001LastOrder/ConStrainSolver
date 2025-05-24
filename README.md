# llm-string-constraints

## Run LLM String Generation
### Run single LLM calls
* Available options:
    * <llm>: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b

```bash
python -m scripts.run_generation string_solver=llm_solver constraint_store=re_full output_folder="outputs/llm/<llm>" string_solver/llm=<llm>
```

### Run LLM with validation
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

### Run LLM with feedback
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

### Run LLM with explanation
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
    * Note: this (1) reads the generated .csv file, (2) validates it line by line and (3) generates a new file which is a copy of the .csv file, extended with a validation column checking whetherthe generated strings actually satify the constraints
    * Note that the file it will read to find the llm outputs is computed from the `output_path`, `llm` and `use_variable_name` arguments, s for the `llm` approach.
```bash
python -m scripts.run_evaluation input_path=outputs/llm_with_validation/2025-02-28_15-52-28/gpt-4o-mini.csv
```

* Run an SMT solver:
```bash
python -m scripts.run_generation --approach smt --file_path=constraint_files/constraints.csv --output_path results/smt --smt_solver=z3
```
