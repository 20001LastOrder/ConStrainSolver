# LLM-based String Generation
> Note: All the following commands assumes that you are in the project root directory.
This module is designed to generate strings that satisfy given constraints using LLMs. Options are described individually for each approach below. In the paper, three different generation approaches are used:
* LLM-only (Direct)
* LLM with validation (+V)
* LLM with feedback (+VF)
* LLM with explanation (+VFE)

### Run single LLM calls (Direct)
* Available options:
    * **llm**: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b

```bash
python -m scripts.run_generation string_solver=llm_solver constraint_store=re_full output_folder="outputs/llm/<llm>" string_solver/llm=<llm>
```

For example, to run gpt-4o-mini:
```bash
python -m scripts.run_generation string_solver=llm_solver constraint_store=re_full output_folder="outputs/llm/gpt-4o-mini" string_solver/llm=gpt-4o-mini
```

### Run LLM with validation (+V)
* Available options:
    * **llm**: gpt-4o-mini_v, gpt-4o_v, deepseek-v3_v, llama3.1-8b_v
    * **validator**: ground_truth_python, ground_truth_smt, hybrid (combine both python and smt validation)

#### Run python or smt
```bash
python -m scripts.run_generation string_solver=llm_solver_with_validation constraint_store=re_full string_solver/validator=<validator> string_solver/llm=<llm> output_folder="outputs/${string_solver.name}/<validator>/<llm>"
```

For example, to run gpt-4o-mini with python validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_validation constraint_store=re_full string_solver/validator=ground_truth_python string_solver/llm=gpt-4o-mini output_folder="outputs/llm_with_validation/python/gpt-4o-mini"
```

#### Run the hybrid approach
```bash
python -m scripts.run_generation string_solver=llm_solver_with_validation constraint_store=re_full string_solver/validator=<validator> string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/${string_solver.name}/<validator>/<llm>"
```

For example, to run gpt-4o-mini with hybrid validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_validation constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=gpt-4o-mini +string_solver.hybrid=True output_folder="outputs/llm_with_validation/hybrid/gpt-4o-mini"
```

### Run LLM with feedback (+VF)
* Available options:
    * **llm**: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b
    * **validator**: ground_truth_python, ground_truth_smt, hybrid (combine both python and smt validation)

#### Run python or smt
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=<validator> string_solver/llm=<llm> output_folder="outputs/${string_solver.name}/<validator>/<llm>"
```

For example, to run gpt-4o-mini with python validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_python string_solver/llm=gpt-4o-mini output_folder="outputs/llm_with_feedback/python/gpt-4o-mini"
```

#### Run the hybrid approach
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/${string_solver.name}/hybrid/<llm>"
```

For example, to run gpt-4o-mini with hybrid validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=gpt-4o-mini +string_solver.hybrid=True output_folder="outputs/llm_with_feedback/hybrid/gpt-4o-mini"
```

### Run LLM with explanation (+VFE)
* Available options:
    * **llm**: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b
    * Each validator takes slightly different arguments (see below)

#### Run python validator
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_python string_solver/llm=<llm> output_folder="outputs/llm_solver_with_explanation/python/<llm>" +string_solver.with_explanation=True
```

For example, to run gpt-4o-mini with python validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_python string_solver/llm=gpt-4o-mini output_folder="outputs/llm_solver_with_explanation/python/gpt-4o-mini" +string_solver.with_explanation=True
```

#### Run smt validator
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=<llm> output_folder="outputs/llm_solver_with_explanation/smt/<llm>" +string_solver.with_explanation=True +string_solver.validator.produce_failed_constraints=True
```

For example, to run gpt-4o-mini with smt validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=gpt-4o-mini output_folder="outputs/llm_solver_with_explanation/smt/gpt-4o-mini" +string_solver.with_explanation=True +string_solver.validator.produce_failed_constraints=True
```

#### Run hybrid validator
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/llm_solver_with_explanation/hybrid/<llm>" +string_solver.with_explanation=True
```

For example, to run gpt-4o-mini with hybrid validation:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback constraint_store=re_full string_solver/validator=ground_truth_smt string_solver/llm=gpt-4o-mini +string_solver.hybrid=True output_folder="outputs/llm_solver_with_explanation/hybrid/gpt-4o-mini" +string_solver.with_explanation=True
```


## Generation with generated constraints
Run hybrid validator with explanation using generated constraints (same configuration as used in the paper)

* Available options:
    * **llm**: gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b
    * **llm_generation** (which llm-generated constraints to use): gpt-4o-mini, gpt-4o, deepseek-v3, llama3.1-8b

```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback string_solver/validator=ground_truth_smt string_solver/llm=<llm> +string_solver.hybrid=True output_folder="outputs/generated_constraints/<llm>/vfe/<llm_generation>" +string_solver.with_explanation=True constraint_store=re_generated constraint_store.generated_constraint_file=constraint_files/generated/<llm_generation>-independent.csv
```

For example, to run gpt-4o-mini with hybrid validation using constraints generated by deepseek-v3:
```bash
python -m scripts.run_generation string_solver=llm_solver_with_feedback string_solver/validator=ground_truth_smt string_solver/llm=gpt-4o-mini +string_solver.hybrid=True output_folder="outputs/generated_constraints/gpt-4o-mini/vfe/deepseek-chat" +string_solver.with_explanation=True constraint_store=re_generated constraint_store.generated_constraint_file=constraint_files/generated/deepseek-chat-independent.csv
```

## Move generated results to the results folder
Move the generated results to the results folder for further analysis depending on the LLM and setup used. For example, for gpt-4o-mini with validation using Python, you can run:

```bash
mv outputs/llm_with_validation/python/gpt-4o-mini/gpt-4o-mini.csv results/generation_with_gt/validation/python/gpt-4o-mini.csv
```

For gpt-4o-mini using constraints generated by deepseek-v3, you can run:
```bash
mv outputs/generated_constraints/gpt-4o-mini/vfe/deepseek-chat/gpt-4o-mini.csv results/generation_with_generated/deepseek-chat/vfe_gpt-4o-mini.csv
```

## Run Evaluations
Finally, run evaluation on the quality of the generated strings for each csv files in the result folder. For example, for gpt-4o-mini with validation using Python, you can run:

```bash
python -m scripts.run_evaluation input_path=results/generation_with_gt/validation/python/gpt-4o-mini.csv
```