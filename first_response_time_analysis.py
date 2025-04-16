import matplotlib.pyplot as plt
import pandas as pd
import mplcyberpunk
from datetime import datetime
from typing import List

import config
from data_loader import DataLoader
from model import Issue, Event, State


class FirstResponseTimeAnalysis:
    """
    Measures time from issue creation to first response (comment, mention, reference, or assignment),
    and provides charts and statistics.
    """

    def __init__(self):
        self.USER = config.get_parameter("user")

    def run(self):
        plt.style.use("cyberpunk")

        issues: List[Issue] = DataLoader().get_issues()

        response_times = []
        label_groups = []

        for issue in issues:
            if not issue.created_date:
                continue

            response_events = [
                e for e in issue.events
                if e.event_type in {"commented", "referenced", "assigned", "mentioned"}
                and e.event_date
                and e.author != issue.creator
            ]

            if response_events:
                first_event = min(response_events, key=lambda e: e.event_date)
                response_time = (first_event.event_date - issue.created_date).total_seconds() / 3600  # in hours

                response_times.append({
                    "issue_number": issue.number,
                    "title": issue.title,
                    "first_response_hours": response_time,
                    "created_date": issue.created_date,
                    "responder": first_event.author
                })

                for label in issue.labels:
                    label_groups.append({
                        "label": label,
                        "first_response_hours": response_time
                    })

        df = pd.DataFrame(response_times)
        label_df = pd.DataFrame(label_groups)

        if df.empty:
            print("No valid response time data found.")
            return

        # === Basic Stats ===
        avg_response = df["first_response_hours"].mean()
        median_response = df["first_response_hours"].median()
        print(f"\n Average first response time: {avg_response:.2f} hours")
        print(f"Median first response time:  {median_response:.2f} hours")

        # === Plot 1: Histogram ===
        plt.figure(figsize=(10, 6))
        plt.hist(df["first_response_hours"], bins=30, edgecolor="white")
        plt.title("Histogram of First Response Time (hours)")
        plt.xlabel("Response Time (hours)")
        plt.ylabel("Number of Issues")
        mplcyberpunk.add_glow_effects()

        # === Plot 2: Label-wise Response Time ===
        if not label_df.empty:
            label_stats = label_df.groupby("label")["first_response_hours"].mean().sort_values()

            plt.figure(figsize=(12, 6))
            label_stats.plot(kind="barh")
            plt.title("Average First Response Time by Label")
            plt.xlabel("Avg Response Time (hours)")
            plt.ylabel("Label")
            mplcyberpunk.add_glow_effects()

        # === Plot 3: Trend Over Time ===
        df["created_month"] = df["created_date"].dt.to_period("M").astype(str)
        monthly_avg = df.groupby("created_month")["first_response_hours"].mean()

        if not monthly_avg.empty:
            plt.figure(figsize=(10, 5))
            monthly_avg.plot(marker='o')
            plt.title("Average First Response Time Over Time")
            plt.xlabel("Month")
            plt.ylabel("Avg Response Time (hours)")
            mplcyberpunk.add_glow_effects()

        # === Show All Plots at Once ===
        plt.show()

        # === Top 5 Slowest Responses ===
        print("Top 5 Slowest First Responses:")
        slowest = df.sort_values("first_response_hours", ascending=False).head(5)
        for _, row in slowest.iterrows():
            print(f"Issue #{row['issue_number']} — {row['first_response_hours']:.2f} hours (by {row['responder']})")


# To run directly
if __name__ == "__main__":
    FirstResponseTimeAnalysis().run()
