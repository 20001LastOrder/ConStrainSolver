# Check if an argument was provided
if [ -z "$1" ]; then
  echo "Please provide an argument."
  exit 1
fi

python -m scripts.run_llm --approach validate --file_path=constraint_files/constraints.csv --output_path "$1" --llm gpt-4o-mini

python -m scripts.run_llm --approach validate --file_path=constraint_files/constraints.csv --output_path "$1" --llm gpt-4o

# python -m scripts.run_llm --approach validate --file_path=constraint_files/constraints.csv --output_path "$1" --llm llama3.1-8b-instruct-q4_0

python -m scripts.run_llm --approach validate --file_path=constraint_files/constraints.csv --output_path "$1" --llm gpt-4o-mini --use_variable_name

python -m scripts.run_llm --approach validate --file_path=constraint_files/constraints.csv --output_path "$1" --llm gpt-4o --use_variable_name 

# python -m scripts.run_llm --approach validate --file_path=constraint_files/constraints.csv --output_path "$1" --llm llama3.1-8b-instruct-q4_0 --use_variable_name