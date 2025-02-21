## Constraint Generator Demo (Week 2)

### How to run
1. Install the required packages from the project root.
2. Ensure you have defined a OPENAI_API_KEY in your environment variables. If not and if you don't want to set it, you can add the following line at the beginning of `constrain_generator/main.py`:
```python
import os

os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
```
3. Run `llm_string/constraint_generator/demos/demo.py`

#### What's new

- The generator now contains a feedback loop that automatically retries the generation process if it fails.
  - This is done by catching the exception thrown and adding it to the LLM prompt as history.
  - You can control the number of attempts allowed by setting the `max_retries` variable in `constraint_generator/main.py`.
  - With a maximum of two retries allowed, the success rate of the LLM increased from 13/30 (43%) to 18/30 (60%).
    - See `constraint_generator/logs` for the logs of the demo runs. 
    - Note that some "succeeded" constraints are still logically incorrect. For example, a common mistake is to take "if A then B" logic as "A and B", thus when a string does not satisfy A, the condition will evaluate to unsatisfied, while it is actually satisfied.
- Logging. This is useful for mass testing and debugging.
  - You can control whether logging should also print on the command line by setting the `verbose` variable in `constraint_generator/main.py`.
- `automated_main.py`, a small automation script to run multiple constraints at once.
  - to change the constraints, modify the `constraints` list in `automated_main.py`.




### Work in progress

To help you quickly understand what's done and what's not, here's a summary of the current status of the project:

| Feature                                               | Implemented  | Tested       |
|-------------------------------------------------------|--------------|--------------|
| NL to SMT-LIB2 constraint                             | ✅            | ✅            |
| NL to Z3Py constraint                                 | ✅            | ✅            |
| Constraint satisfiability validation                  | ✅            | ✅            |
| Multi-variable constraints                            | ✅            | ❌            |
| Feedback loop when generation failed                  | ✅            | ✅            |
| Logging                                               | ✅            | ✅            |
| Examples testing (correctness check)                  | ❌            | ❌            |
| Iterative genetic selection                           | Low priority | Low priority |
| LLM toolkit to teach LLM about constraint expressions | Low priority | Low priority |