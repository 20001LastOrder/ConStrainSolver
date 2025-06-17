## Dataset for the artifacts
This folder contains the dataset using in the paper for experiments. It contains the following files:
* `generated`: The constraints with generated checkers from each LLM used in the paper
* `raw`: The raw constraint files for each constraint type, as well as the ground truth SMT and python checkers for each constraint
* `constraints.csv`: The transformed constraints in the `raw` folder in CSV format. It contains the following columns:
  * sample_id: The ID of the sample
  * Name: The name of the constraint type
  * NL description: The natural language description of the constraints
  * NL negation: The natural language negation of the constraints
  * SMT-LIB2: The SMT-Lib format of the constraints
  * SMT-LIB2 negation: The SMT-Lib negation of the constraints
  * Functions: The python checkers for the constraints