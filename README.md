# GDG Demo: LLM Code Quality Evaluation

A demo pipeline that uses Claude to **generate** Python code from task descriptions and then uses Claude again as a **judge** to score that code against a human-written reference. Built for a Google Developer Group talk on LLM-as-a-judge evaluation.

The demo compares two prompting strategies — a deliberately weak "basic" prompt vs. an "advanced" expert-developer prompt — and runs a paired t-test on the resulting similarity scores.

## What it does

1. Loads a CSV of coding tasks with human-written reference solutions.
2. Asks Claude to solve each task twice: once with a basic prompt, once with an advanced prompt.
3. Asks Claude (acting as a senior Python architect) to score each AI solution against the human reference on a 0–100% similarity scale.
4. Aggregates the scores, displays per-row comparisons in Jupyter, and runs a paired t-test on basic vs. advanced.
5. Writes the full results back to CSV.

## Requirements

- Python 3.9+
- An Anthropic API key

Python packages:

```
anthropic
pandas
python-dotenv
scipy
ipython
```

Install with:

```bash
pip install anthropic pandas python-dotenv scipy ipython
```

## Setup

1. Clone the repo.
2. Create a `.env` file in the project root containing your API key:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Make sure `GDG_Demo_Pipeline.csv` is in the same folder as the script. The CSV needs these columns:
   - `Example` — short label for the row
   - `Task Description` — the prompt given to the code-generator
   - `Human_Written_Code` — the reference solution

## How to run

The script uses `# %%` cell markers, so it runs cleanly in **VS Code's interactive window**, **Jupyter**, or as a plain Python script.

- **Interactive (recommended for the demo):** open in VS Code with the Python extension and "Run All Cells", or run cell-by-cell to walk through the parts.
- **Script:** `python GDG_Demo_Pipeline.py`

## Structure

The script is organised into six parts:

- **Part 1** — defines `get_llm_score()`, which prompts Claude to compare two code snippets and return a similarity percentage.
- **Part 2** — defines `generate_ai_code()`, which generates a Python solution from a task description using either the basic or advanced prompt.
- **Part 3** — loops over every row and generates both basic and advanced AI solutions.
- **Part 4** — loops over every row and scores both AI solutions against the human reference.
- **Part 5** — prints per-row scores, average scores, and renders side-by-side code comparisons in Markdown.
- **Part 6** — writes results to `GDG_Demo_Pipeline_Results.csv` and runs a paired t-test on the two score columns.

## Output

- `GDG_Demo_Pipeline_Results.csv` — original input plus four new columns: `AI_Code_Basic`, `AI_Code_Advanced`, `Score_Basic`, `Score_Advanced`.
- Inline Jupyter output: summary stats, per-row code comparisons, and a paired t-test (t-statistic, p-value, significance at 95%).

## Configuration

The key knobs are at the top of the script:

```python
WORKING_DIR = ...                  # folder containing the CSV
FILE_NAME   = "GDG_Demo_Pipeline.csv"
MODEL       = "claude-sonnet-4-5"
```

Both the generator and the judge are called with `temperature=0` for reproducibility.

## Caveats (worth saying out loud during the talk)

This is a teaching demo, not a rigorous evaluation. A few things to keep in mind:

- **Same model judging its own output.** The judge and the generator are both Claude, with the human code framed as the "gold standard." That bakes in a bias toward human-similar style and inflates apparent quality. For real evals, use a different model family as the judge (or score on independent rubrics like unit-test pass rate and complexity metrics).
- **Similarity ≠ quality.** The rubric assumes human code is well written.
- **The basic prompt is a strawman.** It explicitly tells the model to write inefficient code, so the advanced-vs-basic gap is partly self-inflicted.
- **Small n.** With only a handful of rows, the paired t-test has very low statistical power. Treat the p-value as illustrative, not conclusive — which is, deliberately, part of the lesson.

## Troubleshooting

- **`529 overloaded_error`:** Anthropic's servers are under load. The script initialises the client with retries, but if it still fails, wait a few minutes and re-run. Results are cached to CSV between parts.
- **`NameError: __file__ is not defined`:** you're running interactively. The script handles this by falling back to `Path.cwd()`, so make sure your kernel was started in the project folder.
- **`Format Error` in score columns:** the judge returned something the regex couldn't parse. Uncomment the debug `print` in `get_llm_score()` to see the raw response.

## License

Demo code, use freely.