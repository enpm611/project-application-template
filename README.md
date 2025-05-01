# 📊 GitHub Issues Analyzer

This project is a Python-based application designed to fetch, analyze, and visualize GitHub issues from a repository. It is built with modularity and extensibility in mind and it allows users to extract insights through multiple forms of analysis such as resolution time, label distribution, and user contribution patterns.

---

## 🗂️ Project Structure

```
project-application-template/
├──config                  # JSON config and loader
│   ├── config.json
│   ├── config.py
│ 
├── data                   # Sample issue JSON data
│   ├── closed_issues.json
│   ├── poetry.json
│
├── diagrams/              # UML/Class diagrams and ERDs
│   ├── class-diagram.svg
│   ├── class-diagram.txt
│   ├── erd.svg
│   └── erd.txt
│
├── docs/                  # Requirements and documentation links
│   ├── repository_link.txt
│   ├── requirements.txt
│
├── gui/                   # Optional GUI component using tkinter
│   └── flexible_bucket_gui.py
│
├── models/                # Store Data models
│   └── model.py
│
├── results/               # Analysis output (graphs)
│    ├── graphs/                
│       ├── LabelCountAnalysisGraph.png
│       ├── ResolutionTimeAnalysisGraph.png
│       └── UserIssuesAnalysisGraph.png     
│
├── scripts/               # Core scripts for analysis
│   ├── resolution_time.py
│   ├── label_count.py
│   └── user_issues.py
│
├── tests/                 # Unit tests
│   ├── test_resolution_time.py
│   ├── test_label_count.py
│   └── test_user_issues.py                                      
│
├── utils/                 # Utility modules
│   ├── data_extractors.py
│   ├── plot_utils.py
│   ├── logging_utils.py
│   └── json_utils.py
│
├── README.md              # Project documentation  
│            
└── run.py                 # Main entry point

```

---

## ⚙️ Setup & Installation

### 🔧 Prerequisites
- Python 3.12+
- `pip` package manager
- GitHub personal access token (for API scraping)

### 📦 Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # for MacOS
source venv/Scripts/activate  # for Windows
pip install -r docs/requirements.txt
```

---

## 📐 Design Artifacts

Located in the `diagrams/` folder:
- `class-diagram.svg` / `.txt`
- `erd.svg` / `.txt`

These diagrams describe the system architecture and data relationships.

---

## 📤 Data Collection

To extract GitHub issues and store them as JSON:

```bash
python scripts/scraping_issues.py
```

This script uses GitHub's API to pull issues and saves them as `poetry.json` in the `data/` folder.

---

### 🧰 Utility Modules

Located in: `utils/`

| File              | Purpose                                              |
|-------------------|------------------------------------------------------|
| `data_loader.py`  | Loads issues from JSON using config file             |
| `plot_utils.py`   | Reusable function to plot bar charts using Matplotlib|
| `logging_utils.py`| Configures centralized logging                       |

These utilities are used across all three feature scripts for consistency and modularity.

---

## 🖼️ GUI Module (Feature 1)

Located in: `gui/flexible_bucket_gui.py`

This script powers the **resolution time GUI** launched by:

```bash
python run.py --feature 1
```

**What it does:**
- Opens a Tkinter-based window
- Allows the user to define resolution time buckets
- Displays a bar chart with issue counts in each bucket

**Requirements:**
- Python with `tkinter` and `matplotlib` installed
- GUI support (use Python 3.9–3.12 from python.org version on macOS for best results)

---

## 🚀 Running the Application

Run any analysis script using:

```bash
python run.py --feature 1   # Launch GUI
python run.py --feature 2   # Label count analysis
python run.py --feature 3   # User contribution analysis
```

If you want to use the tkinter-based GUI (requires a display environment):

```bash
python gui/flexible_bucket_gui.py
```

---

## 🧪 Running Tests & Coverage

```bash
python -m coverage run -m unittest discover -s tests
python -m coverage report --omit="test_*.py"
python -m coverage html --omit="test_*.py" # Generate HTML report
open htmlcov/index.html  # View coverage GUI in browser (macOS)
start htmlcov/index.html  # View coverage GUI in browser (Windows)
```

---

## 📈 Visual Output

Graphical results are saved in the `results/graphs/` folder:
- 📊 `ResolutionTimeAnalysisGraph.png`
- 🏷️ `LabelCountAnalysisGraph.png`
- 👤 `UserIssuesAnalysisGraph.png`

---

## 🤝 Contributors

- Divya Kamila
- Heena Khan
- Vineet Agarwal
- Yixun Sindy

---