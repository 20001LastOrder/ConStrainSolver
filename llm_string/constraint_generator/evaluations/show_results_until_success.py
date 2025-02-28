import subprocess
import sys

while True:
    result = subprocess.run([sys.executable, "llm_string/constraint_generator/evaluations/show_results.py"])
    if result.returncode == 0:
        print("Execution successful. Exiting loop.")
        break
    else:
        print(f"Execution failed with code {result.returncode}. Retrying...")