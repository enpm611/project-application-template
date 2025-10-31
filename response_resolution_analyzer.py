"""
Performs response and resolution time analysis on GitHub issues.
"""

from typing import List
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import Issue, Event
import config


class ResponseResolutionAnalyzer:
    """
    Analyzes issue response and resolution times.
    """

    def __init__(self):
        """
        Constructor
        """
        # Optional: can be filtered by user/label if needed later
        self.USER = config.get_parameter('user')
        self.LABEL = config.get_parameter('label')

    # -------------------------------------------------------------
    # Main entrypoint
    # -------------------------------------------------------------
    def run(self):
        """
        Executes the analysis and produces plots + summary statistics.
        """
        issues: List[Issue] = DataLoader().get_issues()

        response_times = self.get_first_response_times(issues)
        resolution_times = self.get_resolution_times(issues)

        self.print_summary_statistics(response_times, resolution_times)
        self.plot_response_time_histogram(response_times)
        self.plot_response_vs_resolution_scatter(response_times, resolution_times)

    # -------------------------------------------------------------
    # Core Computations
    # -------------------------------------------------------------
    def get_first_response_times(self, issues):
        """
        Computes time (in hours) between issue creation and first non-creator comment event.
        """
        response_times = {}
        for issue in issues:
            if not hasattr(issue, "events") or not issue.events:
                continue

            creator = getattr(issue, "creator", None)
            created_time = getattr(issue, "created_date", None)
            if not created_time:
                continue

            comment_times = []
            for e in issue.events:
                if hasattr(e, "event_type") and e.event_type.lower() == "commented":
                    # author = getattr(e, "author", None)
                    # if author is None or author != creator:
                    comment_times.append(e.event_date)

            if comment_times:
                first_response = min(comment_times)
                delta = first_response - created_time
                response_times[issue.number] = delta.total_seconds() / 3600  # hours

        return response_times

    def get_resolution_times(self, issues):
        """
        Computes time (in hours) from issue creation to closing.
        """
        resolution_times = {}
        for issue in issues:
            created_time = getattr(issue, "created_date", None)
            updated_time = getattr(issue, "updated_date", None)
            state = getattr(issue, "state", "").lower()

            if created_time and updated_time and state == "closed":
                delta = updated_time - created_time
                resolution_times[issue.number] = delta.total_seconds() / 3600

        return resolution_times

    # -------------------------------------------------------------
    # Output and Visualization
    # -------------------------------------------------------------
    def print_summary_statistics(self, response_times, resolution_times):
        """
        Prints summary statistics for response and resolution times.
        """
        def summary(title, data):
            print(f"\n--- {title} ---")
            if not data:
                print("No data available.")
                return
            arr = np.array(list(data.values()))
            print(f"Count: {len(arr)}")
            print(f"Mean: {np.mean(arr):.2f} hrs")
            print(f"Median: {np.median(arr):.2f} hrs")
            print(f"Min: {np.min(arr):.2f} hrs")
            print(f"Max: {np.max(arr):.2f} hrs")

        summary("Response Time Summary", response_times)
        summary("Resolution Time Summary", resolution_times)

    def plot_response_time_histogram(self, response_times, bins=None):
        """
        Plots histogram of first response times.
        """
        if not response_times:
            print("No response time data to plot.")
            return

        bins = bins or [1, 6, 24, 72, 168, 336, 720]  # hours
        plt.figure(figsize=(8, 5))
        plt.hist(list(response_times.values()), bins=bins, edgecolor='black')
        plt.title("Distribution of First Response Times (hours)")
        plt.xlabel("Response Time (hours)")
        plt.ylabel("Number of Issues")
        plt.grid(axis='y', alpha=0.6)
        plt.tight_layout()
        plt.show()

    def plot_response_vs_resolution_scatter(self, response_times, resolution_times):
        """
        Scatter plot comparing response time vs resolution time.
        """
        common = set(response_times.keys()) & set(resolution_times.keys())
        if not common:
            print("No overlapping data for scatter plot.")
            return

        x = [response_times[i] for i in common]
        y = [resolution_times[i] for i in common]

        plt.figure(figsize=(7, 5))
        plt.scatter(x, y, alpha=0.7)
        plt.title("Response Time vs Resolution Time")
        plt.xlabel("First Response Time (hours)")
        plt.ylabel("Resolution Time (hours)")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()
