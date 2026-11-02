from collections import defaultdict
from statistics import median
import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import State
"""
Feature 1 Analysis Module  -  run.py feature 1
"""

class Feature1Analysis:

    def __init__(self):
        self.issues = DataLoader().get_issues()

    def get_resolution_date(self, issue):
        """Find the date the issue was closed."""

        closing_events = []

        for event in issue.events:
            if (
                event.event_type
                and "clos" in event.event_type.lower()
                and event.event_date is not None
            ):
                closing_events.append(event.event_date)

        if not closing_events:
            return None

        return max(closing_events)

    def calculate_resolution_times(self):
        """Group issue resolution times by label."""

        label_resolution_times = defaultdict(list)

        closed_issues = 0
        missing_close_dates = 0

        for issue in self.issues:

            if issue.state != State.closed:
                continue

            closed_issues += 1

            if issue.created_date is None:
                continue

            close_date = self.get_resolution_date(issue)

            if close_date is None:
                missing_close_dates += 1
                continue

            resolution_days = (
                close_date - issue.created_date
            ).total_seconds() / 86400
            
            if resolution_days < 0:
                continue

            for label in issue.labels:

                if isinstance(label, str) and label.strip():
                    label_resolution_times[label].append(
                        resolution_days
                    )

        print(f"\nTotal issues: {len(self.issues)}")
        print(f"Closed issues: {closed_issues}")
        print(f"Closed issues without a closing event: {missing_close_dates}")

        return label_resolution_times

    def run(self):

        label_data = self.calculate_resolution_times()

        if not label_data:
            print("\nNo issues with usable resolution dates and labels were found.")
            return

        results = {}

        for label, resolution_times in label_data.items():

            results[label] = median(resolution_times)

        # sorts the labels by median resolution time.
        sorted_results = sorted(
            results.items(),
            key=lambda item: item[1]
        )

        print("\nLABEL RESOLUTION ANALYSIS")
        print("-" * 55)

        for label, days in sorted_results:
            print(f"{label:<30} {days:>20.2f}")

        # generates the following bar chart.
        labels = [item[0] for item in sorted_results]
        resolution_days = [item[1] for item in sorted_results]

        plt.figure(figsize=(12, 6))

        plt.bar(labels, resolution_days)

        plt.title("Median Issue Resolution Time by Label")
        plt.xlabel("Issue Label")
        plt.ylabel("Median Days to Close")

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        plt.show()
 





^G Help          ^O Write Out     ^F Where Is      ^K Cut           ^T Execute       ^C Location      M-U Undo         M-A Set Mark     M-] To Bracket   M-B Previous     ◂ Back           ^◂ Prev Word
^X Exit          ^R Read File     ^\ Replace       ^U Paste         ^J Justify       ^/ Go To Line    M-E Redo         M-6 Copy         ^B Where Was     M-F Next         ▸ Forward        ^▸ Next Word
