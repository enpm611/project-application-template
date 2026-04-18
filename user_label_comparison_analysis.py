"""
Feature 3: User vs. Overall Label Comparison Analysis
"""

from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

import config
from data_loader import DataLoader
from model import Issue


class UserLabelComparisonAnalysis:

    def __init__(self):
        self.user: Optional[str] = config.get_parameter("user")

    def run(self):
        if not self.user:
            print("Feature 3 requires --user.  Example: python run.py --feature 3 --user nishantjr")
            return

        issues: List[Issue] = DataLoader().get_issues()

        user_issues = [i for i in issues if i.creator == self.user]
        if not user_issues:
            print(f"No issues found for user '{self.user}'.")
            return

        overall_dist = self._label_distribution(issues)
        user_dist    = self._label_distribution(user_issues)

        self._print_summary(user_dist, overall_dist, len(user_issues), len(issues))
        self._plot_comparison(user_dist, overall_dist)

    def _label_distribution(self, issues: List[Issue]) -> Dict[str, float]:
        counts: Dict[str, int] = {}
        total = 0

        for issue in issues:
            labels = issue.labels if issue.labels else ["unlabeled"]
            for lbl in labels:
                if isinstance(lbl, dict):
                    lbl = lbl.get("name", "unlabeled")
                lbl = str(lbl).strip()
                counts[lbl] = counts.get(lbl, 0) + 1
                total += 1

        if total == 0:
            return {}

        return {lbl: 100.0 * cnt / total for lbl, cnt in counts.items()}

    def _print_summary(self, user_dist, overall_dist, user_issue_count, total_issue_count):
        print(f"\n=== User vs. Overall Label Comparison: {self.user} ===")
        print(f"User issues : {user_issue_count}")
        print(f"Total issues: {total_issue_count}")

        if not user_dist:
            print("No label data available for this user.")
            return

        top_label   = max(user_dist, key=user_dist.get)
        user_pct    = user_dist[top_label]
        overall_pct = overall_dist.get(top_label, 0.0)

        print(f"\nTop label for {self.user}: '{top_label}'")
        print(f"  {self.user}'s issues with this label : {user_pct:.1f}%")
        print(f"  Project-wide issues with this label : {overall_pct:.1f}%")

        diff      = user_pct - overall_pct
        direction = "higher" if diff >= 0 else "lower"
        print(f"  → {abs(diff):.1f} percentage points {direction} than the project average")

        all_labels = sorted(set(user_dist) | set(overall_dist))
        print(f"\n{'Label':<35} {'User %':>8} {'Overall %':>10} {'Diff':>8}")
        print("-" * 65)
        for lbl in all_labels:
            u = user_dist.get(lbl, 0.0)
            o = overall_dist.get(lbl, 0.0)
            print(f"{lbl:<35} {u:>7.1f}% {o:>9.1f}% {u - o:>+8.1f}%")

    def _plot_comparison(self, user_dist, overall_dist):
        all_labels = sorted(
            set(user_dist) | set(overall_dist),
            key=lambda lbl: user_dist.get(lbl, 0.0),
            reverse=True,
        )

        user_vals    = [user_dist.get(lbl, 0.0)    for lbl in all_labels]
        overall_vals = [overall_dist.get(lbl, 0.0) for lbl in all_labels]

        y          = np.arange(len(all_labels))
        bar_height = 0.35

        fig, ax = plt.subplots(figsize=(12, max(6, len(all_labels) * 0.45)))

        bars_user    = ax.barh(y + bar_height / 2, user_vals,    bar_height,
                               label=self.user,          color="#4C72B0", alpha=0.85)
        bars_overall = ax.barh(y - bar_height / 2, overall_vals, bar_height,
                               label="Overall project",  color="#DD8452", alpha=0.85)

        for bar in bars_user:
            w = bar.get_width()
            if w > 0.5:
                ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2,
                        f"{w:.1f}%", va="center", fontsize=8)

        for bar in bars_overall:
            w = bar.get_width()
            if w > 0.5:
                ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2,
                        f"{w:.1f}%", va="center", fontsize=8)

        ax.set_yticks(y)
        ax.set_yticklabels(all_labels, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel("Percentage of issues (%)")
        ax.set_title(f"Label Distribution: {self.user} vs. Overall Project")
        ax.legend(loc="lower right")
        ax.set_xlim(0, max(max(user_vals, default=0), max(overall_vals, default=0)) * 1.15 + 5)

        plt.tight_layout()
        plt.show()
