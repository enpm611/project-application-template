import matplotlib.pyplot as plt
import mplcursors  # For interactive hover tooltips
import mplcyberpunk  # For a stylish Matplotlib theme
import pandas as pd
import numpy as np
from typing import List
from datetime import datetime

import config
from data_loader import DataLoader
from model import Issue, Event, State


class CycleTimeAnalysis:
    """
    Implements cycle time analysis for issues labeled 'kind/bug' and marked as 'closed'.
    Uses an interactive histogram where hovering shows bin values.
    """

    def __init__(self):
        """
        Constructor: You can add additional parameters if needed.
        """
        # Optional parameter from config
        self.USER = config.get_parameter("user")

    def run(self):
        # Apply the cyberpunk style for a more appealing aesthetic
        plt.style.use("cyberpunk")

        # 1) Load issues
        issues: List[Issue] = DataLoader().get_issues()

        # 2) Filter issues: labeled 'kind/bug' and state=closed
        filtered_issues = [
            i for i in issues
            if (i.state == State.closed) and ("kind/bug" in i.labels)
        ]
        print(f"Found {len(filtered_issues)} closed issues labeled 'kind/bug'.")

        # 3) Compute cycle times
        cycle_times = []
        for issue in filtered_issues:
            # Attempt to find a 'closed' event date
            closed_event = next((e for e in issue.events if e.event_type == "closed"), None)
            if closed_event and closed_event.event_date:
                closed_date = closed_event.event_date
            else:
                # Fallback: updated_date often matches the close date for closed issues
                closed_date = issue.updated_date

            if issue.created_date and closed_date:
                cycle_time_days = (closed_date - issue.created_date).days
                cycle_times.append({
                    "issue_number": issue.number,
                    "title": issue.title,
                    "cycle_time_days": cycle_time_days
                })

        df = pd.DataFrame(cycle_times)
        if df.empty:
            print("No issues found or no valid dates for cycle time calculations.")
            return

        # 4) Basic stats
        avg_cycle_time = df["cycle_time_days"].mean()
        median_cycle_time = df["cycle_time_days"].median()
        print(f"Average cycle time (days): {avg_cycle_time:.2f}")
        print(f"Median cycle time (days):  {median_cycle_time:.2f}")

        # 5) Repeated/related bug detection (naive)
        def normalize_title(title: str) -> str:
            return ''.join(ch.lower() for ch in title if ch.isalnum() or ch.isspace())
        df["normalized_title"] = df["title"].apply(normalize_title)

        df_grouped = (
            df.groupby("normalized_title")
            .size()
            .reset_index(name="count")
            .sort_values(by="count", ascending=False)
            .head(10)
        )
        print("\nTop repeated/related bug titles (naive grouping):")
        print(df_grouped)

        ################################################################
        # 6) Plot 1: Interactive Histogram for Cycle Times
        ################################################################
        plt.figure(figsize=(10, 6))
        counts, bin_edges, patches = plt.hist(
            df["cycle_time_days"],
            bins=30,
            edgecolor="white"
        )
        plt.title("Histogram of Cycle Times (days)\nfor 'kind/bug' Issues (Closed)")
        plt.xlabel("Cycle Time (days)")
        plt.ylabel("Count of Issues")

        # Use mplcyberpunk's glow effects
        mplcyberpunk.add_glow_effects()

        # Make the histogram interactive with mplcursors
        cursor = mplcursors.cursor(patches, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            """
            When the user hovers over a bar, show the bin range and count.
            """
            idx = sel.index  # which bar (patch) the user is hovering
            c = counts[idx]  # how many issues in that bin
            left_edge = bin_edges[idx]
            right_edge = bin_edges[idx + 1]
            sel.annotation.set_text(
                f"Count: {c:.0f}\nRange: {left_edge:.1f} - {right_edge:.1f} days"
            )

        ################################################################
        # 7) Plot 2: Bar chart of top repeated bug groups
        ################################################################
        plt.figure(figsize=(10, 6))
        plt.bar(df_grouped["normalized_title"], df_grouped["count"], edgecolor="white")
        plt.title("Top Repeated Bug Titles (Naive Grouping)")
        plt.xlabel("Normalized Title")
        plt.ylabel("Count of Issues")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        mplcyberpunk.add_glow_effects()

        # Show both figures now, with the histogram being interactive
        plt.show()


if __name__ == "__main__":
    CycleTimeAnalysis().run()
