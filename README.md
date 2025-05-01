## 📦 Project: GitHub Issues Analyzer

This project is a Python-based application designed to fetch, analyze, and visualize GitHub issues from a repository. It allows users to extract insights using three core features: label distribution, resolution time categorization, and user participation activity.

---

### 📁 Project Structure

```
project-application-template/
├── run.py                      # Main entry point
├── config/                     # JSON config and loader
├── data/                       # Input JSON data
├── diagrams/                  # Class diagrams and ERDs
├── docs/                       # Documentation and requirements
├── models/                     # Data models
├── results/graphs/             # Analysis result images
├── scripts/                    # Feature modules
├── utils/                      # Reusable utility modules
```

---

### 🚀 Features

| Feature ID | Description                          | Run Command Example                  |
|------------|--------------------------------------|--------------------------------------|
| Feature 1  | Label Count Analysis                 | `python run.py --feature 1`          |
| Feature 2  | Resolution Time GUI (Tkinter-based)  | `python run.py --feature 2`          |
| Feature 3  | User Issues Activity Analysis        | `python run.py --feature 3`          |

---

### ⚙️ Configuration

Located in: `config/config.json`

```json
{
    "ENPM611_PROJECT_DATA_PATH":"path/to/data/file.json"
}
```

You can modify this file to point to different datasets if needed.

---

### 📊 Output

Visualizations are saved to:
```
results/graphs/
├── LabelCountAnalysisGraph.png
├── ResolutionTimeAnalysisGraph.png
└── UserIssuesAnalysisGraph.png
```

---

### 🧩 Dependencies

Install requirements:
```bash
pip install -r docs/requirements.txt
```

Make sure `matplotlib` and `tkinter` (GUI) are working. For macOS, use Python ≥ 3.10 from [python.org](https://www.python.org) for full GUI support.

---

### 📐 Design Artifacts

Located in the `diagrams/` folder:
- `class-diagram.svg` / `.txt`
- `erd.svg` / `.txt`

These diagrams describe the system architecture and data relationships.

---

### 📤 Data Collection

To extract GitHub issues and store them as JSON:

```bash
python scripts/scraping_issues.py
```

This script uses GitHub's API to pull issues and saves them as `poetry.json`.

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

### 🖼️ GUI Module (Feature 2)

Located in: `gui/flexible_bucket_gui.py`

This script powers the **resolution time GUI** launched by:

```bash
python run.py --feature 2
```

**What it does:**
- Opens a Tkinter-based window
- Allows the user to define resolution time buckets
- Displays a bar chart with issue counts in each bucket

**Requirements:**
- Python with `tkinter` and `matplotlib` installed
- GUI support (use Python from python.org on macOS for best results)

---


