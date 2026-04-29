# ENPM611 Project – GitHub Issue Analysis

## Overview

This project analyzes GitHub issues from an open-source repository dataset and generates insights into issue activity, contributor behavior, and trends over time.

The application processes issue data from a JSON file and provides multiple analysis features that can be run from the command line.

## Setup Instructions

### Clone the Repository

Run:

```
git clone https://github.com/Adelco24/project-application-template.git
cd project-application-template
```

### Install Dependencies

```
pip install -r requirements.txt
```

### Configure Data Path

Ensure config.json contains:

```
{
"ENPM611_PROJECT_DATA_PATH": "poetry_issues.json"
}
```

## Running the Application

All analyses are run using:

```
python run.py --feature <number>
```

### Optional arguments:

Filter by contributor:
```
--user <username>
```

Filter by label:
```
--label <label>
```

## Features

### Feature 0: Example Analysis

Command:

```
python run.py --feature 0
```

Description:

- Displays total number of events across issues
- Shows a bar chart of top issue creators

### Feature 1: Label Activity Analysis

Commands:

```
python run.py --feature 1
python run.py --feature 1 --label Bug
```

Description:

- Analyzes issue activity based on labels
- Can filter by a specific label
- Outputs:
  - number of matching issues
  - most common labels
  - most common event types
- Displays:
  - bar chart of event type distribution

### Feature 2: Contributor Activity Analysis

Commands:

```
python run.py --feature 2
python run.py --feature 2 --user <username>
```

Description:

- Analyzes contributor activity across issues and events
- Can focus on a specific contributor
- Outputs:
  - number of issues created
  - number of events authored
  - event type breakdown
- Displays:
  - bar chart of event types for a contributor or top contributors overall

### Feature 3: Issue Trend Analysis

Command:

```
python run.py --feature 3
```

Description:

- Provides overall insights into issue trends
- Outputs:
  - total number of issues
  - open vs closed issue counts
  - average events per issue
  - top labels
  - issue creation trends over time
- Displays:
  - bar chart of most common labels

## Project Structure

run.py
config.py
data_loader.py
model.py
example_analysis.py
label_activity_analysis.py
contributor_activity_analysis.py
issue_trend_analysis.py

## Notes

- The dataset is loaded once and reused for performance
- Charts are generated using matplotlib
- Features support optional filtering using command-line arguments
