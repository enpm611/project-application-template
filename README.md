# ENPM611 Team 1: Poetry Issue Analyzer

A command-line application that analyzes the GitHub issues of the open-source
[Poetry](https://github.com/python-poetry/poetry) project (issue and event data
provided as a JSON file). It answers three questions about how issues are
labeled, who works on them, and how issue activity changes over time, and shows
the results as console output and matplotlib charts.

This repository is a fork of the ENPM611 application template. The design
diagrams from Milestone 1 are in [`docs/`](docs/).

## Setup

**Python version:** Python 3.10 or newer (developed and tested with Python 3.12).

**Dependencies:** `python-dateutil`, `numpy`, `pandas`, `matplotlib`
(listed in `requirements.txt`).

1. Clone this repository.
2. Create and activate a virtual environment in the repository root:
   - macOS / Linux: `python3 -m venv venv && source venv/bin/activate`
   - Windows (PowerShell): `python -m venv venv; venv\Scripts\Activate.ps1`
3. Install the dependencies: `pip install -r requirements.txt`

### Configure the dataset path

Download the issues JSON file from the project assignment in Canvas. Then tell
the application where it is, using **either** way (the environment variable
takes priority and keeps your personal path out of the repository):

- Environment variable (recommended)
  - macOS / Linux: `export ENPM611_PROJECT_DATA_PATH=/path/to/poetry_issues.json`
  - Windows (PowerShell): `$env:ENPM611_PROJECT_DATA_PATH="C:\path\to\poetry_issues.json"`
- or edit `ENPM611_PROJECT_DATA_PATH` in `config.json` (do not commit your personal path).

Do not commit the data file. If the path is missing or wrong, the application
prints a clear error message instead of crashing.

## Running the features

```
python run.py --feature 1                    # label comparison (all labels)
python run.py --feature 1 --label kind/bug   # one label in detail
python run.py --feature 2                    # contributor activity (whole project)
python run.py --feature 2 --user abn         # one contributor vs. the top contributors
python run.py --feature 3                    # activity trends over time
python run.py --feature 0                    # template example analysis
```

The label (`kind/bug`) and user (`abn`) above are examples from the Poetry
dataset. Use a label or user that exists in **your** dataset file: label names
and contributors differ between datasets. `--label` and `--user` are optional
and case-insensitive. If the label or user
is not found, the application suggests similar names and exits cleanly.
Charts open in a matplotlib window; close the window to continue (feature 2
shows two charts, one after the other).

## The three analyses

Every analysis prints its **question**, **method** and **finding** to the console.

### Feature 1: Label resolution (`label_resolution_analysis.py`)

_Feature 1 owner: replace this line with the question, run commands, method, output and limitations of feature 1._

### Feature 2: Contributor activity (`contributor_activity_analysis.py`)

_Feature 2 owner: replace this line with the question, run commands, method, output and limitations of feature 2._

### Feature 3: Discussion trends (`discussion_trend_analysis.py`)

_Feature 3 owner: replace this line with the question, run commands, method, output and limitations of feature 3._

## Known limitations and assumptions

- **Bots are excluded** (authors ending in `[bot]`) from comment, contributor
  and response-time statistics.
- **Time to close** uses the date of the last `closed` event. Closed issues
  without a closing event in the data (20 of 401 in `poetry_issues.json`) and
  open issues are left out of timing statistics. Reopened issues use their latest close.
- **Triage** (feature 2): labels and closes made by the issue's own reporter are
  not counted, because issue templates attribute automatic labels to the
  reporter and reporters closing their own issue is not triage work.
- **First response** is the first human comment by someone other than the
  issue creator. **Time to triage** only counts issues whose `status/triage`
  label was actually removed; issues closed while still marked "triage" are not
  included.
- **Triagers** (feature 3) are people with at least 5 label or close actions on
  issues they did not report.
- **Subset vs. full dataset:** the provided subset (`poetry_issues.json`) is not
  representative over time: almost all of its closings are in 2024, which makes
  the closed/opened ratio and early-year statistics unreliable. Feature 3 prints
  a warning when this happens. Running the analyses on `poetry_issues_all.json`
  gives noticeably different results (for example in the first-response
  concentration); always state which file a result comes from.
- Most issues in the dataset are from 2024, so earlier years have few issues
  and their medians are less reliable (years with fewer than 10 issues are not
  used in the first-vs-last comparison). The final quarter may be incomplete.
- Medians for labels with few resolved issues are unreliable; feature 1 only
  compares labels with at least 5 resolved issues.
- If a dataset has too few issues with a closing event (no label with at least 5
  timed issues), feature 1 falls back to comparing discussion per label only and
  says so.
- Results depend on the dataset file used.

## Differences from the Milestone 1 design

- `model.py` gained small helpers shared by all analyses (`Event.is_human`,
  `Issue.closed_date`, `Issue.days_to_close()`, `Issue.human_comments()`) instead
  of duplicating this logic in each analysis.
- `data_loader.py` raises a clear error when the data path is not configured;
  `run.py` now has a `main()` function and reports that error cleanly.
- Feature 2 does more than the Milestone 1 sequence diagram shows: it also
  prints a written finding after the correlations, computes first-reply
  concentration (extra table and a third chart), and prints a message and exits
  when the requested user does not exist. The component structure is unchanged.
- The three analysis modules also import `model.py` (for `Issue`), which the
  component diagram does not show.

## Team contributions

Each member describes their own work in their own subsection below (edit only
your own subsection and your own feature section above).

### [Member 1: name]

_Replace this line with what this member implemented and contributed._

### [Member 2: name]

_Replace this line with what this member implemented and contributed._

### [Member 3: name]

_Replace this line with what this member implemented and contributed._