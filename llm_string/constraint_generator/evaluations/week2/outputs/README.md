### Setup

All tests are carried out with `gpt-4o-mini` and a `max_retries_per_attempt` of 2 (i.e. maximum 3 calls before failing a step).

In the current directory you'll find summarizing tables on all the results, where `batch_size` is the number of constraints per batch of generation.

You'll also find the raw data in the `{x}_batch` directories, where `x` is the batch size.
- the first folders are run_ids used to distinguish between runs, you can ignore them.
- within the folder you'll find the following files:
  - config.json: the configuration used for the run.
  - output.csv: the postprocessed results of the run. Contains the constraints generated after each step.
  - results.csv: the calculated matrix of output.csv.
  - plot.png: a plot of the historical accuracy progress of the run.
  - table.txt: a table summarizing the accuracy of each step of the run.

### Terminology

- **First step accuracy**: accuracy of the constraints after the first step, i.e. after the very first attempt.
- **Final accuracy**: accuracy of the constraints at termination.
  - Termination is defined as the {batch_size * 5}th step, which gives an overall equal number of LLM calls for all test cases.
- **Evaluated per constraint**: each constraint is evaluated independently on its recall and precision.
- **Evaluated per batch**: the constraints are evaluated on the batch in which they get generated. If any of the constraint is syntactically incorrect, the whole batch is considered incorrect. If all of them are syntactically correct, each constraint is then evaluated independently on its semantic precision.
  - This means that for batch of size 1, evaluated per constraint and per batch are the same.

### Interpretation

- From the tables and the graphs, we observe that the number of steps taken has a less significant impact than we expected.
  - This can be explained by the fact that constraint generation steps are independent between them. If a step fails, the next attempt is not influenced by the previous one.
  - For batch size 4, most attempts to constraint generation never reach a final accepted set of answer. So the different steps are literally just "failing and retying", without any significant improvement.
  - If we're looking to improve accuracy through more LLM calls, we may try to increase `max_retries_per_attempt` as retry information is carries over within the same attempt (step).
- Batch size influences the results, but not in a linear way.
  - The results from batches of size 2 are comparable to that of size 1. But the results of batch 4 are significantly worse.