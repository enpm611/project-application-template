
# ENPM611 Poetry Issues Analysis

This repository contains an application for analyzing **GitHub Issues** from the [`python-poetry/poetry`](https://github.com/python-poetry/poetry) repository. The application retrieves issues, stores them in a local JSON file, and provides multiple insights via command-line features and matplotlib charts.

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Features](#features)  
   - [Feature 1: Issue Lifespan and Stats by Label](#feature-1-issue-lifespan-and-stats-by-label)  
   - [Feature 2: Label vs. Number of Comments](#feature-2-label-vs-number-of-comments)  
   - [Feature 3: Pie Chart of Label Distribution](#feature-3-pie-chart-of-label-distribution)  
3. [Fetching Data](#fetching-data)  
4. [Installation and Setup](#installation-and-setup)  
5. [Usage](#usage)  
6. [Examples](#examples)
7. [Repository Structure](#repository-structure)  
7. [App Functionality](#app-functionality)  


## Project Overview

For this project, we focus on analyzing how issues evolve in the `python-poetry` repository. Our goal is to uncover meaningful insights about the labels, contributors, and life cycles of issues. We look at:

- **Time to implement or resolve issues**  
- **Number of comments and contributors involved**  
- **Distribution of issues by labels**  


## Features

### Feature 1: Issue Lifespan and Stats by Label
- **Input**: A label of interest from the given list (e.g., `bug`, `enhancement`, etc.).  
- **Output**:  
  - Average issue lifespan for that label  
  - Average number of comments  
  - Number of contributors involved  
- **Purpose**: Helps identify how long it typically takes to resolve issues with certain labels and how active they are.

### Feature 2: Label vs. Number of Comments
- **Input**: *No special argument required*.  
- **Output**: Couple of bar charts showing the total number of comments for top 15 labels and yearly trend of area label. Also including couple of line charts to shoe the trend of bug and features.  
- **Purpose**: Quickly see which labels drive the most discussion or have the highest engagement and different trends over the years since repo was created.

### Feature 3: Pie Chart of Label Distribution
- **Input**: *No special argument required by default.*  
- **Output**: Several pie charts (e.g., for labels prefixed `kind/`, `status/`, `area/`) showing how issues are distributed by those label categories.  
- **Purpose**: Visual snapshot of how many issues fall under each “kind,” “status,” or “area” category.


## Fetching Data

We provide a script **`fetch_issues.py`** that uses the GitHub API to download all issues (including timeline events) from `python-poetry/poetry` and save them to `poetry_data.json`. 

1. **Set your GitHub Token**  
   - Create a `.env` file in the project root (same level as `fetch_issues.py`) with the line:  
     ```
     GITHUB_TOKEN=your_personal_access_token
     ```
   - This token must have sufficient scopes to read public repository data.  
2. **Run the fetch script**  
   ```bash
   python fetch_issues.py
   ```
3. **Check the output**  
   - A new file named `poetry_data.json` is generated, containing the issues and their events.


## Installation and Setup

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Karen-W-2002/enpm611-project.git
   cd enpm611-project
   ```
2. **(Optional) Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **(Optional) Prepare `.env` file** if you plan to run `fetch_issues.py`.
   ```bash
   GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
   ```


## Usage

After installation, you can run any of the analysis features using:

```bash
python run.py --feature <FEATURE_NUMBER>
```

## Examples
### Feature 1
Example output table of a specific label:
![](/assets/feature1_input1.png)

Example output table of all labels:
![](/assets/feature1_input2.png)

Example output charts for all labels (top 10):
![](/assets/feature1_chart_issuelifespan.png)
![](/assets/feature1_chart_contributors.png)
![](/assets/feature1_chart_comments.png)

### Feature 2
Example output bar chart for top 15 labels according to number of comments:
![](/assets/feature2_chart_top15_comments.png)

Example output charts for yearly trends:
![](/assets/feature2_chart_areaLabelPerYear.png)
![](/assets/feature2_chart_bugTrend.png)
![](/assets/feature2_chart_featureTrend.png)

### Feature 3
Example output pie charts for different labels distribution:
![](/assets/feature3_pie_kindLabel.png)
![](/assets/feature3_pie_statusLabel.png)
![](/assets/feature3_pie_areaLabel.png)

## Repository Structure

```
├── fetch_issues/
│   └── fetch_issues.py
│   └── poetry_data.json
├── tests/
│   └── test_anaylsis_one.py
│   └── test_config.py
│   └── test_feature2.py
│   └── test_pieChart_Labels.py
├── assets/
│   └── feature1_chart_comments.png
│   └── feature1_input1.png
│   └── feature1_chart_contributors.png
│   └── feature1_input2.png
│   └── feature1_chart_issuelifespan.png
│   └── feature2_chart_bugTrend.png
│   └── feature2_chart_featureTrend.png
│   └── feature2_chart_areaLabelPerYear.png
│   └── feature2_chart_top15_comments.png
│   └── feature3_pie_areaLabel.png
│   └── feature3_pie_kindLabel.png
│   └── feature3_pie_statusLabel.png
├── analysis_one.py
├── config.py
├── config.json
├── data_loader.py
├── fetch_issues.py
├── feature2.py
├── model.py
├── pieChart_Labels.py
├── requirements.txt
├── run.py
└── README.md
```

## Testing

1. **Run all test cases**:
   ```bash
   python -m coverage run -m unittest discover -s tests
   ```
2. **Get coverage report in terminal**:
   ```bash
   python -m coverage report --omit="test_*"
   ```
3. **Get detailed HTML coverage report**:
   ```bash
   coverage html  --omit="test_*"
   ```


## App Functionality
The parser implements these functions:
- `fetch_issues.py`: This script retrieves all issues from the python-poetry/poetry GitHub repository using the GitHub REST API. It fetches issue metadata, including labels, state, assignees, and timestamps, as well as a detailed timeline of events (e.g., labeling, commenting). The timeline enriches each issue with historical context.
The issues are paginated and rate-limit aware, ensuring safe and complete data extraction. All formatted issues are saved to poetry_data.json for later analysis.

This application implements these functions:
- `data_loader.py`: Utility to load the issues from the provided data file and returns the issues in a runtime data structure (e.g., objects)
- `model.py`: Implements the data model into which the data file is loaded. The data can then be accessed by accessing the fields of objects.
- `config.py`: Supports configuring the application via the config.json file. You can add other configuration paramters to the config.json file.
- `run.py`: This is the module that will be invoked to run your application. Based on the --feature command line parameter, one of the three analyses you implemented will be run. You need to extend this module to call other analyses.

The analysis implements these functions:
- `analysis_one.py`: Performs an input which is a label-based analysis on GitHub issues. For each label, it calculates:
  - Average issue lifespan (in hours)
  - Average number of comments
  - Number of contributors (issue creators + event authors)

  The results are presented in a table, and the user can choose to view stats for a specific label or all labels. If "all" is selected, a bar chart is generated to visualize the top 10 labels by average lifespan.
  
  This analysis helps identify which labels are associated with longer-running or more complex discussions.
- `feature2.py`: Analyzes GitHub issue data to visualize the total number of comments per label and yearly trend of different labels.

   - Loads issues from poetry_data.json

   - Tallies comment counts from timeline events for each label

   - Generates a bar chart showing the top 15 labels based on total comment activity

   - Generates a bar chart and line charts to show yearly trend for different area labels and yearly activities in bug and features

  This helps identify which labels (and by proxy, which types of issues) drive the most discussion or engagement in the repository.
- `pieChart_Labels.py`: Generates pie charts to visualize the distribution of GitHub issues by label categories. Specifically focuses on labels that start with:

    - kind/ (e.g., bug, feature)

    - status/ (e.g., needs info, triaged)

    - area/ (e.g., packaging, dependencies)

    For each category:

    - Filters and counts labels with the matching prefix

    - Displays a pie chart showing percentage distribution

    - Adds exact counts and labels to the legend for clarity

    This helps reveal where most issues are concentrated in terms of type, progress status, and functional area.
