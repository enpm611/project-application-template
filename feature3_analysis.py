from typing import List
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue


DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


class SeasonalPatternAnalysis:
    """
    Analyzes seasonal and weekly patterns in GitHub issue activity.
    Plots issue creations, referenced events, and closures by day-of-week
    and month-of-year in a 2x3 subplot grid.
    """

    def run(self):
        """
        Loads all issues and plots seasonal/weekly activity patterns.
        """
        issues: List[Issue] = DataLoader().get_issues()

        df_create = self._extract_creations(issues)
        df_ref = self._extract_referenced(issues)
        df_close = self._extract_closures(issues)

        print(f'\nCreations: {len(df_create)}  |  Referenced Events: {len(df_ref)}  |  Closures: {len(df_close)}\n')

        fig, axes = plt.subplots(3, 2, figsize=(14, 12))
        fig.suptitle('Seasonal & Weekly Patterns in Issue Activity', fontsize=14)

        rows = [
            (df_create, 'Issue Creations'),
            (df_ref, 'Referenced Events (Engagement)'),
            (df_close, 'Issue Closures'),
        ]

        for row_idx, (df, label) in enumerate(rows):
            day_counts = df['day_of_week'].value_counts().reindex(range(7), fill_value=0)
            ax = axes[row_idx][0]
            ax.bar(range(7), day_counts.values)
            ax.set_xticks(range(7))
            ax.set_xticklabels(DAY_LABELS)
            ax.set_title(f'{label} by Day of Week')
            ax.set_xlabel('Day of Week')
            ax.set_ylabel('Count')

            month_counts = df['month'].value_counts().reindex(range(1, 13), fill_value=0)
            ax = axes[row_idx][1]
            ax.bar(range(12), month_counts.values)
            ax.set_xticks(range(12))
            ax.set_xticklabels(MONTH_LABELS, rotation=45)
            ax.set_title(f'{label} by Month')
            ax.set_xlabel('Month')
            ax.set_ylabel('Count')

        plt.tight_layout()
        plt.show()

    def _extract_creations(self, issues: List[Issue]) -> pd.DataFrame:
        """Returns DataFrame with day_of_week and month for each issue creation."""
        records = []
        for issue in issues:
            if issue.created_date is not None:
                records.append({
                    'day_of_week': issue.created_date.weekday(),
                    'month': issue.created_date.month,
                })
        return pd.DataFrame(records, columns=['day_of_week', 'month'])

    def _extract_referenced(self, issues: List[Issue]) -> pd.DataFrame:
        """Returns DataFrame with day_of_week and month for each referenced event."""
        records = []
        for issue in issues:
            for event in (issue.events or []):
                if event.event_type == 'referenced' and event.event_date is not None:
                    records.append({
                        'day_of_week': event.event_date.weekday(),
                        'month': event.event_date.month,
                    })
        return pd.DataFrame(records, columns=['day_of_week', 'month'])

    def _extract_closures(self, issues: List[Issue]) -> pd.DataFrame:
        """Returns DataFrame with day_of_week and month for each closed event."""
        records = []
        for issue in issues:
            for event in (issue.events or []):
                if event.event_type == 'closed' and event.event_date is not None:
                    records.append({
                        'day_of_week': event.event_date.weekday(),
                        'month': event.event_date.month,
                    })
        # Note: 'closed' events include both closed issues and merged/closed PRs
        return pd.DataFrame(records, columns=['day_of_week', 'month'])


if __name__ == '__main__':
    SeasonalPatternAnalysis().run()
