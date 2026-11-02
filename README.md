## Feature 1: Label Resolution Analysis

### Purpose
Analyzes how long issues take to resolve by grouping closed issues according to their labels and calculating the median resolution time for each label.

### How It Works
1. Loads the project issue data.
2. Identifies closed issues with valid creation dates and closing events.
3. Calculates the number of days between issue creation and closure.
4. Groups resolution times by issue label.
5. Calculates the median resolution time for labels with at least five resolved issues.
6. Displays the results in a bar chart.

### Visualization
The bar chart compares median issue resolution times across labels.

- **X-axis:** Issue labels.
- **Y-axis:** Median days to close.

### How to Run

Set the environment variable to the location of your issue JSON file (example using Git Bash):

```bash
export ENPM611_PROJECT_DATA_PATH="$HOME/Downloads/poetry_issues.json"
```

Run Feature 1:

```bash
python run.py --feature 1
```

### Files Added or Modified
- `label_resolution.py` — Implements the Label Resolution Analysis.
- `run.py` — Connects Feature 1 to the command-line application.
