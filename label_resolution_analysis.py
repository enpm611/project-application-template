from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

import config
from data_loader import DataLoader
from model import Issue, State


class LabelResolutionAnalysis:
    """
    Feature 1:
    - Filter issues by a user-provided label
    - Print percentage of all issues with that label
    - Print median time to completion for that label
    - Plot a resolution-time distribution for that label
    - Plot the same distribution for all issues for comparison
    """

    def __init__(self):
        self.label: Optional[str] = config.get_parameter("label")

    def run(self):
        if not self.label:
            print("Feature 1 requires --label.")
            return

        issues: List[Issue] = DataLoader().get_issues()
        total_issues = len(issues)

        if total_issues == 0:
            print("No issues found.")
            return

        label_issues = [issue for issue in issues if self._issue_has_label(issue, self.label)]
        label_pct = 100.0 * len(label_issues) / total_issues

        label_resolution_days = self._resolution_days(label_issues)
        all_resolution_days = self._resolution_days(issues)

        print(f"Label: {self.label}")
        print(f"Issues with this label: {len(label_issues)} / {total_issues} ({label_pct:.2f}%)")

        if label_resolution_days:
            print(f"Median time to completion: {np.median(label_resolution_days):.2f} days")
        else:
            print("Median time to completion: unavailable (no resolved issues with this label)")

        self._plot_distributions(label_resolution_days, all_resolution_days)

    def _issue_has_label(self, issue: Issue, label: str) -> bool:
        target = label.strip().lower()
        for existing in issue.labels:
            if isinstance(existing, dict):
                existing = existing.get("name", "")
            if str(existing).strip().lower() == target:
                return True
        return False

    def _resolution_days(self, issues: List[Issue]) -> List[float]:
        durations: List[float] = []

        for issue in issues:
            if issue.created_date is None:
                continue

            resolved_date = self._resolved_date(issue)
            if resolved_date is None:
                continue

            delta_days = (resolved_date - issue.created_date).total_seconds() / 86400.0
            if delta_days >= 0:
                durations.append(delta_days)

        return durations

    def _resolved_date(self, issue: Issue):
        if issue.state != State.closed:
            return None

        closed_event_dates = []
        for event in issue.events:
            if event.event_date is None:
                continue

            event_type = (event.event_type or "").strip().lower()
            if event_type in {"closed"}:
                closed_event_dates.append(event.event_date)

        if closed_event_dates:
            return min(closed_event_dates)

        return issue.updated_date

    def _plot_distributions(self, label_days: List[float], all_days: List[float]):
        fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharex=True, sharey=True)

        bins = self._shared_bins(label_days, all_days)

        self._plot_single_hist(
            axes[0],
            label_days,
            bins,
            f"Resolution time for label: {self.label}"
        )
        self._plot_single_hist(
            axes[1],
            all_days,
            bins,
            "Resolution time for all issues"
        )

        fig.supxlabel("Time to resolve (days)")
        fig.supylabel("Percentage of issues")
        fig.tight_layout()
        plt.show()

    def _shared_bins(self, label_days: List[float], all_days: List[float]):
        combined = label_days + all_days
        if not combined:
            return 1

        max_day = max(combined)
        if max_day <= 0:
            return 1

        bin_count = min(20, max(5, int(np.sqrt(len(combined)))))
        return np.linspace(0, max_day, bin_count + 1)

    def _plot_single_hist(self, ax, days: List[float], bins, title: str):
        if not days:
            ax.set_title(title)
            ax.text(
                0.5,
                0.5,
                "No resolved issues to plot",
                ha="center",
                va="center",
                transform=ax.transAxes
            )
            ax.set_xlabel("Time to resolve (days)")
            ax.set_ylabel("Percentage of issues")
            return

        weights = np.ones(len(days)) * 100.0 / len(days)
        ax.hist(days, bins=bins, weights=weights, edgecolor="black")
        ax.set_title(title)
        ax.set_xlabel("Time to resolve (days)")
        ax.set_ylabel("Percentage of issues")