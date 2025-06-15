# llm-string-constraints

Artifacts for the paper *"LLM-based Satisfiability Checking of String Requirements by Consistent Data and Checker Generation"*

## Artifact Summary
This repository contains code to run the LLM-based string constraint generation from natural language requirements and generating string values using natural language constraints. It also contains the dataset used in the paper, which is a collection of string constraints and their corresponding checkers in Python and SMT-Lib format. Finally, the scripts to run the constraint generation and string generation used in the paper as well as notebooks to reproduce tables / figures from the paper are provided. 

The artifact can also be customized in the following ways using configuration through [Hydra](https://hydra.cc/docs/intro/):
* Use different local or remote LLMs for the generation of constraints and strings
* Use different validation approaches of the generated strings
* Use different SMT solvers for the validation of the generated strings


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

Note: you must have corresponding API keys in your environment variables (e.g. OPENAI_API_KEY for GPT models) for the LLM calls to work properly.

## Artifact Location:
The repository is available at:

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


# License
The code and data in this repository are licensed under the [MIT License](./LICENSE). 
