import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from typing import List
from datetime import datetime

# External library for stylish Matplotlib themes
# Make sure to install with: pip install mplcyberpunk
import mplcyberpunk

import config
from data_loader import DataLoader
from model import Issue, Event, State

class CycleTimeAnalysis:
    """
    Implements cycle time analysis for issues labeled 'kind/bug' and marked as 'closed'.
    Uses mplcyberpunk to provide a more visually appealing style to Matplotlib plots.
    """

    def __init__(self):
        """
        Constructor: You can add additional parameters if needed.
        """
        # Optional parameter from config (similar to example_analysis)
        self.USER = config.get_parameter("user")

    def run(self):
        """
        Main entry point to run the cycle time analysis.
        """
        # Apply the mplcyberpunk style for our entire session
        plt.style.use("cyberpunk")

        # 1) Load issues
        issues: List[Issue] = DataLoader().get_issues()

        # 2) Filter relevant issues (kind/bug, state=closed)
        filtered_issues = [
            i for i in issues
            if (i.state == State.closed) and ("kind/bug" in i.labels)
        ]

        print(f"Found {len(filtered_issues)} closed issues labeled 'kind/bug'.")

        # 3) Compute cycle times
        cycle_times = []
        for issue in filtered_issues:
            # Attempt to find a 'closed' event date in the timeline:
            closed_event = next((e for e in issue.events if e.event_type == "closed"), None)
            if closed_event and closed_event.event_date:
                closed_date = closed_event.event_date
            else:
                # Fallback: if the issue is closed, updated_date is typically the same as the close date
                closed_date = issue.updated_date

            if issue.created_date and closed_date:
                cycle_time_days = (closed_date - issue.created_date).days
                cycle_times.append({
                    "issue_number": issue.number,
                    "title": issue.title,
                    "created_date": issue.created_date,
                    "closed_date": closed_date,
                    "cycle_time_days": cycle_time_days
                })

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(cycle_times)

        # 4) Basic Stats
        if not df.empty:
            avg_cycle_time = df["cycle_time_days"].mean()
            median_cycle_time = df["cycle_time_days"].median()
            print(f"Average cycle time (days): {avg_cycle_time:.2f}")
            print(f"Median cycle time (days): {median_cycle_time:.2f}")
        else:
            print("No issues found or no valid dates for cycle time calculations.")
            return

        # 5) Simple repeated/related bug detection (naive example)
        #    Group by simplified titles.
        def normalize_title(title: str) -> str:
            return ''.join(e.lower() for e in title if e.isalnum() or e.isspace())

        df["normalized_title"] = df["title"].apply(normalize_title)

        # Group by normalized title (very naive approach)
        df_grouped = df.groupby("normalized_title").size().reset_index(name="count")
        df_grouped = df_grouped.sort_values(by="count", ascending=False).head(10)

        print("\nTop repeated/related bug titles (naive grouping):")
        print(df_grouped)

        ###################################################################
        # 6) Visualization: Use mplcyberpunk style for both plots.
        ###################################################################

        # (A) Cycle Time Histogram
        plt.figure(figsize=(10, 6))
        plt.hist(df["cycle_time_days"], bins=30, edgecolor="white")
        plt.title("Histogram of Cycle Times (days)\nfor 'kind/bug' Issues (Closed)")
        plt.xlabel("Cycle Time (days)")
        plt.ylabel("Count of Issues")
        # Add neat glow effects from mplcyberpunk
        mplcyberpunk.add_glow_effects()

        # (B) Bar chart of top repeated bug groups
        plt.figure(figsize=(10, 6))
        plt.bar(df_grouped["normalized_title"], df_grouped["count"], edgecolor="white")
        plt.title("Top Repeated Bug Titles (Naive Grouping)")
        plt.xlabel("Normalized Title")
        plt.ylabel("Count of Issues")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        mplcyberpunk.add_glow_effects()

        # Display both plots together
        plt.show()


if __name__ == "__main__":
    # For local debugging, you can directly run this file:
    CycleTimeAnalysis().run()
