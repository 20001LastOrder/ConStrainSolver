## Constraint Generator Demo (Week 1)

### How to run
1. Install the required packages from the project root.
2. Ensure you have defined a OPENAI_API_KEY in your environment variables. If not and if you don't want to set it, you can add the following line at the beginning of `constrain_generator/main.py`:
```python
import os

os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
```
3. Run `llm_string/constraint_generator/demos/demo.py`

#### Understanding the demo

The demo is a command line interactive program.

After running the program, the first thing you'll see is the following:

```aiignore
Default constraint type:  smt-lib2
Enter the type of constraint you want to generate, or press Enter to use the default constraint type.
Supported types are ['smt-lib2', 'z3py']: 
```

As the prompt suggests, the tool currently supports generation of two types of constraints: `smt-lib2` and `z3py`.

You can choose one of these types by entering the name of the type. If you don't want to change the default type, you can simply press Enter, and `smt-lib2` will be used.

This process of using a default value is implemented for all the prompts in the program.

After selecting the constraint type, you'll be prompted to enter the natural language constraint for which you want to generate the formal constraint. Note that the LLM configuration is very basic for the demo, with currently no tool support nor feedback loop (yet). This means that, the more complex the natural language constraint, the more likely it will throw an exception. The default constraint has been tested to have a high success rate.

Then, the LLM will do its job. After that's done, you'll see the following:

```
Generated constraint:  variables=['name'] constraint='(not (str.suffixof " " name))'
```

This is the generated constraint. The `variables` field shows the variables used in the constraint (FYI, LLM is allowed to define more than one variable given the natural language constraint), and the `constraint` field shows the generated constraint in the previously specified format.

Then we jump into the evaluation phase. Depending on the number of values, you'll be asked again to enter the values for the variables. The default value is again provided for your convenience.

After receiving all values, the program will evaluate whether the values satisfy the constraint and return the result:

```
Sat:  True
```




### Work in progress

To help you quickly understand what's done and what's not, here's a summary of the current status of the project:

| Feature                                               | Implemented  | Tested       |
|-------------------------------------------------------|--------------|--------------|
| NL to SMT-LIB2 constraint                             | ✅            | ✅            |
| NL to Z3Py constraint                                 | ✅            | ✅            |
| Constraint satisfiability validation                  | ✅            | ✅            |
| Multi-variable constraints                            | ✅            | ❌            |
| Feedback loop when generation failed                  | ❌            | ❌            |
| Examples testing (correctness check)                  | ❌            | ❌            |
| Iterative genetic selection                           | ❌            | ❌            |
| LLM toolkit to teach LLM about constraint expressions | Low priority | Low priority |