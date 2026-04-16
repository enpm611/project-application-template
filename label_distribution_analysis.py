import pandas as pd
import matplotlib.pyplot as plt
from typing import List
from data_loader import DataLoader
from model import Issue
import config


class LabelDistributionAnalysis:
    """
    Loads all GitHub issues and displays a heatmap showing the percentage
    distribution of labels per user (top 20 users by issue count).
    """

    def __init__(self):
        self.USER: str = config.get_parameter('user')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        # Build a flat list of (creator, label) records — one row per label per issue.
        # Issues with no labels are recorded as 'unlabeled'.
        # If a specific user is passed via --user, only their issues are included.
        records = []
        for issue in issues:
            if self.USER is not None and issue.creator != self.USER:
                continue
            labels = issue.labels if issue.labels else ['unlabeled']
            for label in labels:
                records.append({'creator': issue.creator, 'label': label})

        if not records:
            print("No issues found.")
            return

        df = pd.DataFrame(records)

        top_n_users = 20
        top_users = df['creator'].value_counts().nlargest(top_n_users).index
        df_top = df[df['creator'].isin(top_users)]

        # Pivot to a creator × label matrix, then normalize each row to 100%
        # so each cell shows what % of that user's issues have a given label
        pivot = df_top.groupby(['creator', 'label']).size().unstack(fill_value=0)
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        im = ax.imshow(pivot_pct.values, aspect='auto', cmap='YlOrRd')

        ax.set_xticks(range(len(pivot_pct.columns)))
        ax.set_xticklabels(pivot_pct.columns, rotation=45, ha='right')
        ax.set_yticks(range(len(pivot_pct.index)))
        ax.set_yticklabels(pivot_pct.index)

        # Annotate each cell with its percentage value
        for i in range(len(pivot_pct.index)):
            for j in range(len(pivot_pct.columns)):
                val = pivot_pct.values[i, j]
                if val > 0:
                    ax.text(j, i, f'{val:.0f}%', ha='center', va='center', fontsize=8)

        plt.colorbar(im, ax=ax, label='% of issues')
        ax.set_title(f'Label Distribution per User')
        ax.set_xlabel('Label')
        ax.set_ylabel('Creator')
        plt.tight_layout()
        plt.show()

    