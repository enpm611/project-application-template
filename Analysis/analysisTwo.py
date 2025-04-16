import os
import gzip
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None

def run(top_n=30):
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Build the full path to your gzipped data file
    data_path = os.path.join(script_dir, "..", "data", "poetry_data.json.gz")

    # Load data from gzipped JSON file
    with gzip.open(data_path, "rt", encoding="utf-8") as f:
        data = json.load(f)

    # Collect label counts and resolution times
    label_counts = defaultdict(int)
    label_res_times = defaultdict(list)

    for issue in data:
        created = parse_date(issue.get("created_at"))
        closed = parse_date(issue.get("closed_at"))
        labels = issue.get("labels", [])
        label_names = [lbl.get("name") for lbl in labels if lbl.get("name")]

        for lbl in label_names:
            label_counts[lbl] += 1
            if created and closed:
                days = (closed - created).total_seconds() / 86400
                label_res_times[lbl].append(days)

    # Prepare DataFrame
    df = pd.DataFrame({
        "label": list(label_counts.keys()),
        "issue_count": list(label_counts.values()),
        "avg_res_days": [
            (sum(label_res_times[lbl]) / len(label_res_times[lbl])) if label_res_times[lbl] else None
            for lbl in label_counts
        ]
    })

    # Filter out labels with no resolution data
    df = df[df['avg_res_days'].notnull()]

    # Sort by issue count
    df = df.sort_values(by='issue_count', ascending=False).head(top_n)

    print(f"\nTop {top_n} labels with issue count and avg resolution time:\n")
    print(df)

    # Plot issue count bars
    plt.figure(figsize=(16, 8))
    bars = plt.bar(df["label"], df["issue_count"], width=0.5, color=plt.cm.plasma(df["issue_count"] / df["issue_count"].max()))

    # Annotate each bar with avg resolution time (rounded, smaller font)
    for bar, res_days in zip(bars, df["avg_res_days"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{int(round(res_days))}d",
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold'
        )

    plt.title(f"Top {top_n} Most Frequent Labels with Avg Resolution Time")
    plt.xlabel("Label")
    plt.ylabel("Number of Issues")
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    run()
