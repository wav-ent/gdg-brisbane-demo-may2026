# %%
# =============================================================================
# GDG Demo: LLM Code Quality Evaluation
# Compares Human vs AI-Generated Python code using Claude as a judge
# =============================================================================

# %% Import Functions
import os
import re
import time
import pandas as pd
import anthropic
from dotenv import load_dotenv
from IPython.display import display, Markdown
from scipy import stats
from pathlib import Path

# %% Configuration

try:
    WORKING_DIR = Path(__file__).parent
except NameError:  # running interactively
    WORKING_DIR = Path.cwd()

FILE_NAME   = "GDG_Demo_Pipeline.csv"
MODEL       = "claude-sonnet-4-5"

# %% Read in Data
exampleData = pd.read_csv(
    os.path.join(WORKING_DIR, FILE_NAME),
    encoding='utf-8',
    skipinitialspace=True
).dropna(how='all')


print(f"Loaded {len(exampleData)} rows")
display(exampleData[['Example', 'Task Description', 'Human_Written_Code']]
        .style
        .set_properties(**{'text-align': 'left', 'white-space': 'pre-wrap'})
        .set_table_styles([{'selector': 'th', 'props': [('text-align', 'left')]}])
        .hide(axis='index')
)

# %% Initialize Anthropic Client
load_dotenv()
client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from .env

# =============================================================================
# PART 1: Define a Function to Score Two Code Snippers (Human vs AI) using Claude
# =============================================================================

# %% Define Scoring Function
def get_llm_score(row, ai_code_col, objective_code_col = 'Human_Written_Code') :
    human_code = row[objective_code_col]
    ai_code    = row[ai_code_col]
    task_desc  = row['Task Description']

    prompt = f"""
    Role: You are a Senior Python Architect and Static Analysis Expert.
    Your task is to perform a structural audit comparing [Human Code] (the gold 
    standard for efficiency) and [AI Code].

    Task Description: {task_desc}

    [Human Code]
    {human_code}

    [AI Code]
    {ai_code}

    Objective: Provide a single Similarity Score (0-100%) based on how closely 
    the AI's underlying logic and structural efficiency mirror the human's code.

    Evaluation Criteria:
    - Structural Alignment: Do the two versions use the same control flow?
    - Algorithmic Parity: Does the AI use the same optimised logic? Penalise 
      heavily for inferior data structures (e.g. list vs set for lookups).
    - Complexity Matching: Penalise unnecessary complexity or code smell.

    Ignore: variable/function names, imports, docstrings, comments, whitespace.

    Output Requirement:
    Respond with ONLY this exact format and nothing else:
    Similarity Score: [X]%
    """

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        output_text = response.content[0].text
       # print(f"\n  DEBUG response: {output_text!r}")  # temporary debug line
        match = re.search(r'Similarity Score:\s*(\d+)\s*%', output_text)
        return f"{match.group(1)}%" if match else "Format Error"

    except Exception as e:
        print(f"  Error scoring row: {e}")
        return "API Error"


# =============================================================================
# PART 2: Run AI Code Generation (Basic and  Advanced Prompt)
# =============================================================================

# %% Define Code Generation Function
def generate_ai_code(row, prompt_type="advanced"):
    """Generate Python code from a task description using Claude."""
    task_desc = row['Task Description']

    prompts = {
        "basic": f"""
        You are learning Python. Your code sometimes works but is not efficient 
        and sometimes makes mistakes.
        Write a simple Python solution for the following task:
        Task: {task_desc}
        Rules:
        - Return ONLY raw Python code
        - No markdown, no code fences, no comments, no docstrings
        """,
        "advanced": f"""
        You are an expert Python developer.
        Write a clean, efficient Python solution for the following task:
        Task: {task_desc}
        Rules:
        - Return ONLY raw Python code
        - No markdown, no code fences, no comments, no docstrings
        """
    }

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=512,
            temperature=0,
            messages=[{"role": "user", "content": prompts[prompt_type]}]
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r'^```[\w]*\n?', '', raw)  # Remove opening ```python or ```
        raw = re.sub(r'\n?```$', '', raw)       # Remove closing ```
        return raw.strip()

    except Exception as e:
        print(f"  Error generating code: {e}")
        return "API Error"

# =============================================================================
# PART 3: Generate Code using Both Basic and Advanced Prompts
# =============================================================================

# %% Define Code Generation Function

print("\n" + "="*60)
print("PART 3: Generating API Code (Basic & Advanced)")
print("="*60)

for index, row in exampleData.iterrows():
    print(f"  Generating code for row {index}...")
    exampleData.at[index, 'AI_Code_Basic']    = generate_ai_code(row, prompt_type="basic")
    exampleData.at[index, 'AI_Code_Advanced'] = generate_ai_code(row, prompt_type="advanced")
    time.sleep(1)

print("Code generation complete!")

# =============================================================================
# PART 4: Score API-Generated Code vs Human
# =============================================================================

# %% Score Both Prompt Types
print("\n" + "="*60)
print("PART 4: Scoring API Code vs Human")
print("="*60)

for index, row in exampleData.iterrows():
    print(f"  Scoring row {index}...")
    exampleData.at[index, 'Score_Basic']    = get_llm_score(row, ai_code_col='AI_Code_Basic')
    exampleData.at[index, 'Score_Advanced'] = get_llm_score(row, ai_code_col='AI_Code_Advanced')
    time.sleep(1)

# =============================================================================
# PART 5: Final Results
# =============================================================================

# %% Print Results
pd.set_option('display.max_colwidth', None)

print("\n" + "="*60)
print("PART 5: Final Results")
print("="*60)
print(exampleData[['Task Description', 'Score_Basic', 'Score_Advanced']].to_string())

baseline_quality_score   = exampleData['Score_Basic'].str.replace('%', '').astype(float).mean()
advanced_quality_score = exampleData['Score_Advanced'].str.replace('%', '').astype(float).mean()


# %% Display Aggregated Scores in Markdown Format (for Jupyter)

display(Markdown(f"### Summary\n- Average Basic Prompt Score: {baseline_quality_score:.1f}%\n- Average Advanced Prompt Score: {advanced_quality_score:.1f}%"))

# %% Display Aggregated Scores in Markdown Format (for Jupyter)

for index, row in exampleData.iterrows():
    display(Markdown(f"## Row {index}: {row['Task Description']}"))
    display(Markdown(f"**Human Written Code:**\n```python\n{row['Human_Written_Code']}\n```"))
    display(Markdown(f"**API Basic Code** — Score: `{row['Score_Basic']}`\n```python\n{row['AI_Code_Basic']}\n```"))
    display(Markdown(f"**API Advanced Code** — Score: `{row['Score_Advanced']}`\n```python\n{row['AI_Code_Advanced']}\n```"))
    display(Markdown("---"))

# %% Write to Disk
print("\n" + "="*60)
print("PART 6: Final Results write to disk")
print("="*60)

exampleData.to_csv(
    os.path.join(WORKING_DIR, "GDG_Demo_Pipeline_Results.csv"),
    index=False,
    encoding='utf-8'
)

# %% Is it stat sig? The importance of a large enough sameple size and paired testing!!


# Convert as arrays (use actual values from your dataframe)
basic_scores    = exampleData['Score_Basic'].str.replace('%', '').astype(float)
advanced_scores = exampleData['Score_Advanced'].str.replace('%', '').astype(float)

# Paired t-test (recommended — since each row has both scores for the same task)
t_stat, p_value = stats.ttest_rel(basic_scores, advanced_scores)

print(f"T-statistic: {t_stat:.4f}")
print(f"P-value:     {p_value:.4f}")
print(f"Significant: {'Yes' if p_value < 0.05 else 'No'} (at 95% confidence)")

# %%
