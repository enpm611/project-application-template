# ENPM611 Group 4: Poetry Issue Activity Analyzer

A command line Python application that analyzes GitHub issues from the [python-poetry/poetry](https://github.com/python-poetry/poetry/issues) open source project and reports insights about how issues are resolved, who does the work, and whether the backlog is growing or shrinking.

The application loads the course data file (about 5,500 issues with their full timelines of comments, labels and close events) and runs one of three analyses, each printing a text report to the terminal and opening a chart.

| Feature | Command | Question it answers |
|---|---|---|
| 1. Label Resolution Analysis | `python run.py --feature 1 [--label LABEL]` | How long do issues with each label take to close, and which labels have the largest open backlog? |
| 2. Contributor Activity Analysis | `python run.py --feature 2 [--user USER]` | Who opens, comments on, labels and closes issues, and what does one contributor's activity look like over time? |
| 3. Issue Trend Analysis | `python run.py --feature 3 [--label LABEL]` | How many issues are opened vs closed each quarter, and how has the open backlog changed? |
| 0. Example Analysis | `python run.py --feature 0 [--user USER]` | Template example: event counts and top issue creators. |

## Setup

### 1. Clone the repository

```
git clone https://github.com/Mac2804/ENPM611_Group-4_Poetry-Issue-Activity.git
cd ENPM611_Group-4_Poetry-Issue-Activity
```

### 2. Create a virtual environment and install dependencies

Requires Python 3.9 or newer.

```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the data file

Download the poetry issues data file (`.json`) from the project assignment in Canvas. Then point the application to it in one of two ways:

* Edit `config.json` and set `ENPM611_PROJECT_DATA_PATH` to the file path, or
* Set an environment variable with the same name, which avoids committing your personal path:

```
export ENPM611_PROJECT_DATA_PATH=/path/to/poetry_issues.json     # macOS / Linux
set ENPM611_PROJECT_DATA_PATH=C:\path\to\poetry_issues.json      # Windows (cmd)
```

Please do not commit the data file to the repository.

## Running the analyses

All analyses are started from the repository root with `run.py`. The `--feature` (or `-f`) flag is required. The optional `--label` (`-l`) and `--user` (`-u`) flags narrow the analysis. Each run first prints the **question** the analysis answers and the **method** it uses, then the results and a **finding**, and finally opens a chart window; close the window to end the program.

Invalid input is handled without crashing: an unknown label or user prints the closest matching names, an unknown feature number prints the valid options, and a missing data file prints how to configure it.

### Feature 1: Label Resolution Analysis

Resolution time is measured from when an issue was created until its last `closed` event (reopened issues use their final close).

```
python run.py --feature 1
```

Compares every label with at least 10 closed issues: number closed and open, median, mean and 90th percentile days to close, and the share of issues still open. Prints the slowest and fastest labels and the largest open backlogs. The chart shows median days to close and open backlog side by side for each label.

```
python run.py --feature 1 --label kind/bug
```

Deep dive into one label: resolution statistics, the share closed within a week, and the oldest issues still open. The chart groups closed issues into time buckets (under a day, up to a week, up to a month, and so on). If the label does not exist, the program suggests the closest matching labels.

### Feature 2: Contributor Activity Analysis

Counts four activities per contributor: issues opened, comments, labels applied and issues closed. Bots (`github-actions[bot]`, `stale[bot]`) and `ghost` (GitHub's placeholder for deleted accounts) are excluded from the rankings.

```
python run.py --feature 2
```

Lists the top 10 contributors by total activity, shows how concentrated each activity is (the share done by the top 5 people), and charts the top 10 contributors for each activity.

```
python run.py --feature 2 --user finswimmer
```

Profile of one contributor: their active period, count and rank for each activity, and their most active year. The chart shows their activity per year, stacked by activity type. If the user is not found, the program suggests similar usernames.

### Feature 3: Issue Trend Analysis

```
python run.py --feature 3
python run.py --feature 3 --label area/docs
```

Builds a quarterly time series (for example `2022Q4`) of issues opened and closed, plus the open backlog at the end of each quarter. Prints a table of every quarter, total opened and closed, the busiest quarters (combined activity, most opened, most closed), the peak backlog, a per year summary and the backlog change over the last 4 quarters. The figure has two charts: issues opened vs closed per quarter (top) and the open backlog per quarter (bottom). With `--label`, only issues carrying that label are included.

The backlog is a running total of opened minus closed, assuming no issues were open before the first quarter in the data.

Closed issues that have no `closed` event in the data use their last updated date as the close date, so the final backlog matches the number of currently open issues.

## Example insights from the data

* **Labels:** `kind/question` and `status/duplicate` issues are closed within hours (median under half a day), while `area/error-handling` and `area/ux` issues take a median of well over a year. `status/triage` holds the largest open backlog (244 issues).
* **Contributors:** commenting is broad (over 5,700 people), but closing is concentrated: the top 5 maintainers closed nearly 60% of all issues.
* **Trend:** the backlog grew every year from 2018 to a peak of 1,020 open issues at the end of 2022Q1, then fell sharply as 2022Q2 to 2022Q4 closed far more issues than were opened (2022Q4 alone closed 527). Over the last 4 quarters (2023Q4 to 2024Q4) the backlog shrank by 224, ending at 317 open issues.

## Known limitations and assumptions

* **Dataset snapshot:** the data covers issues created from February 2018 to October 2024. Results describe that snapshot, not the live repository, and the final quarter (2024Q4) is partial.
* **Close date:** an issue's close date is its last `closed` event, so reopened issues use their final close. About 200 closed issues have no `closed` event in the data. Feature 1 leaves them out of resolution times (the report says how many); Feature 3 uses their last updated date instead so the backlog stays consistent.
* **Labels:** an issue with several labels is counted once under each label, so label groups overlap. Labels are taken as they are at the time of the snapshot; labels removed earlier are not considered. Feature 1 only compares labels with at least 10 closed issues to avoid unreliable medians.
* **Contributors:** activity is attributed to the GitHub username on each event. Bots and deleted accounts (`ghost`) are excluded from rankings, and the same person using two accounts counts as two contributors. Issue templates apply some labels automatically, which credits the issue creator with a "label applied" activity.
* **Resolution time** measures calendar time, not effort, and is skewed by a few very old issues, which is why medians are reported alongside means.

## Team contributions

| Team member | Areas of contribution |
|---|---|
| [Name] | [e.g. Milestone 1 diagrams, Feature 1 implementation, README] |
| [Name] | [e.g. Feature 2 implementation, code review of PRs] |
| [Name] | [e.g. Feature 3 implementation, testing] |
| [Name] | [e.g. README, presentation preparation] |

## Project structure

| File | Purpose |
|---|---|
| `run.py` | Entry point. Parses the command line flags and dispatches to the selected analysis. |
| `config.py` / `config.json` | Configuration. Reads `config.json` and environment variables; command line flags are stored here so every analysis can read them. |
| `data_loader.py` | Loads the JSON data file once and caches the list of `Issue` objects. |
| `model.py` | Data model: `Issue`, `Event` and `State`. `Issue.get_closed_date()` returns when an issue was last closed. |
| `label_resolution_analysis.py` | Feature 1: `LabelResolutionAnalysis`. |
| `contributor_activity_analysis.py` | Feature 2: `ContributorActivityAnalysis`. |
| `issue_trend_analysis.py` | Feature 3: `IssueTrendAnalysis`. |
| `example_analysis.py` | Example analysis provided with the template (feature 0). |
| `milestone1/` | Milestone 1 design: component diagrams (before and after), sequence diagram and repository link. |

Each analysis module can also be run directly, for example `python issue_trend_analysis.py`, which runs it without any filter.

## VSCode run configurations

`.vscode/launch.json` contains run configurations for the example analysis and each feature (with sample `--label` / `--user` values), so the analyses can be started and debugged from the Run and Debug panel. Edit the `args` there to try other labels or users.
