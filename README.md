# GitHub Issue Analysis for Python-Poetry

This application analyzes GitHub issues from the [poetry](https://github.com/python-poetry/poetry) Open Source project and generates interesting insights through various analyses and visualizations.

## Features

The application will implement three different analyses:

1. **Label Analysis** (Feature 1): Analyzes issues based on labels

   - Shows label distribution across all issues
   - Identifies the most active labels (by average comments per issue)
   - Analyzes resolution time for issues with different labels
   - Can focus on a specific label using the `--label` parameter

2. **Contributor Analysis** (Feature 2): Analyzes contributor activity

   - Identifies top contributors by different metrics (issue creation, comments, closing)
   - Analyzes which labels different contributors focus on
   - Shows contributor activity patterns
   - Can focus on a specific contributor using the `--user` parameter

3. **Timeline Analysis** (Feature 3): Analyzes issue activity over time
   - Shows issue creation and closing patterns over time
   - Analyzes issue lifecycle (time to first response, time to resolution)
   - Identifies activity trends and patterns (by day of week, hour of day)

Each analysis provides both textual output to the console and visual charts using matplotlib.

## Setup

### Install dependencies

In the root directory of the application, create a virtual environment, activate that environment, and install the dependencies:

```
pip install -r requirements.txt
```

### Configure the data file

The application uses a JSON file containing GitHub issues data. Update the `config.json` file with the path to your data file:

```json
{
  "ENPM611_PROJECT_DATA_PATH": "path/to/poetry_data.json"
}
```

Alternatively, you can set an environment variable:

```
export ENPM611_PROJECT_DATA_PATH=path/to/poetry_data.json
```

## Running the Analyses

### Label Analysis

To run the label analysis on all issues:

```
python run.py --feature 1
```

To focus on issues with a specific label:

```
python run.py --feature 1 --label "bug"
```

### Contributor Analysis

To run the contributor analysis for all contributors:

```
python run.py --feature 2
```

To focus on a specific contributor:

```
python run.py --feature 2 --user "username"
```

### Timeline Analysis

To run the timeline analysis:

```
python run.py --feature 3
```

### Example Analysis

The original example analysis is still available:

```
python run.py --feature 0
```

## Implementation Details

The application is structured as follows:

- `data_loader.py`: Loads the issues from the JSON data file
- `model.py`: Defines the data model (Issue, Event, State)
- `config.py`: Handles configuration parameters
- `run.py`: Main entry point that runs the specified analysis
- `label_analysis.py`: Implements the label analysis
- `contributor_analysis.py`: Implements the contributor analysis
- `timeline_analysis.py`: Implements the timeline analysis

Each analysis class follows a similar structure:

1. Initialize with any parameters (e.g., label, user)
2. Load the issues data
3. Perform the analysis
4. Output results to the console
5. Generate visualizations using matplotlib
