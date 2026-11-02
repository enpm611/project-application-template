"""
Feature 1: Label Resolution Analysis

Answers: how long do issues with each label take to close, and which
labels have the largest open backlog?

Usage:
    python run.py --feature 1                   # compare all labels
    python run.py --feature 1 --label kind/bug  # analyze one label
"""

import difflib
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

import config
from data_loader import DataLoader
from model import Issue, State


QUESTION = ('How long do issues with each label take to close, and which '
            'labels have the largest open backlog?')
METHOD = ('Resolution time is the number of days from an issue\'s created date to its '
          'last closed event. Open issues, and closed issues without a close event, are '
          'left out of resolution times. Open issues make up the backlog. Labels are '
          'compared only if they have at least 10 closed issues.')

MIN_CLOSED_FOR_COMPARISON: int = 10
TOP_N: int = 5
# Time buckets for the single-label chart: (upper bound in days, bucket name)
TIME_BUCKETS = [
    (1, 'under a day'),
    (7, 'up to a week'),
    (30, 'up to a month'),
    (365, 'up to a year'),
    (float('inf'), 'over a year'),
]


def resolution_days(issue: Issue) -> Optional[float]:
    """
    Days from the issue's creation to its last close, or None if the issue
    is open or has no usable dates.
    """
    closed = issue.get_closed_date()
    if closed is None or issue.created_date is None:
        return None
    created = issue.created_date
    # Dates may be timezone-aware or naive; put both on the same footing
    if (closed.tzinfo is None) != (created.tzinfo is None):
        closed = closed.replace(tzinfo=None)
        created = created.replace(tzinfo=None)
    return (closed - created).total_seconds() / 86400


def issues_with_label(issues: List[Issue], label: str) -> List[Issue]:
    return [issue for issue in issues if label in issue.labels]


def all_labels(issues: List[Issue]) -> List[str]:
    return sorted({label for issue in issues for label in issue.labels})


def build_label_table(issues: List[Issue]) -> pd.DataFrame:
    """
    One row per label with closed and open counts, resolution-time statistics,
    and the share of issues still open. An issue with several labels is
    counted under each of them.
    """
    rows = []
    for label in all_labels(issues):
        subset = issues_with_label(issues, label)
        days = [d for d in (resolution_days(i) for i in subset) if d is not None]
        days_series = pd.Series(days, dtype=float)
        open_count = sum(1 for i in subset if i.state == State.open)
        rows.append({
            'label': label,
            'closed': len(days),
            'open': open_count,
            'median_days': days_series.median(),
            'mean_days': days_series.mean(),
            'p90_days': days_series.quantile(0.9),
            'pct_open': 100 * open_count / len(subset),
        })
    return pd.DataFrame(rows)


class LabelResolutionAnalysis:
    """
    Feature 1: measures how long issues take to close, grouped by label.

    With no --label, compares every label that has at least 10 closed
    issues. With --label, analyzes that single label.
    """

    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--label). None if not given.
        self.label: str = config.get_parameter('label')

    def run(self):
        """
        Starting point for this analysis. Prints the question and method,
        then dispatches to the project-wide comparison or the single-label view.
        """
        issues: List[Issue] = DataLoader().get_issues()

        print(f'\n{QUESTION}\n\nMethod: {METHOD}\n')

        if self.label is None:
            self._compare_all_labels(issues)
        else:
            self._analyze_one_label(issues, self.label)

    def _compare_all_labels(self, issues: List[Issue]):
        """
        Project-wide view: compares labels on resolution time and backlog,
        then prints a finding and charts both measures.
        """
        table = build_label_table(issues)
        table = table[table['closed'] >= MIN_CLOSED_FOR_COMPARISON]
        if table.empty:
            print(f'No label has at least {MIN_CLOSED_FOR_COMPARISON} closed issues.')
            return

        print(f'Labels with at least {MIN_CLOSED_FOR_COMPARISON} closed issues: {len(table)}\n')
        columns = ['label', 'closed', 'open', 'median_days', 'mean_days', 'p90_days', 'pct_open']
        print(table.sort_values('median_days', ascending=False)[columns].round(1).to_string(index=False))

        slowest = table.nlargest(TOP_N, 'median_days')
        fastest = table.nsmallest(TOP_N, 'median_days')
        backlog = table.nlargest(TOP_N, 'open')
        for title, rows in [('Slowest labels (median days to close)', slowest),
                            ('Fastest labels (median days to close)', fastest),
                            ('Largest open backlog', backlog)]:
            print(f'\n{title}:')
            print(rows[['label', 'closed', 'open', 'median_days']].round(1).to_string(index=False))

        top_slow = slowest.iloc[0]
        top_fast = fastest.iloc[0]
        top_backlog = backlog.iloc[0]
        print(f'\nFINDING: "{top_slow.label}" has the slowest median resolution '
              f'({top_slow.median_days:.1f} days over {int(top_slow.closed)} closed issues), '
              f'and "{top_fast.label}" the fastest ({top_fast.median_days:.1f} days). '
              f'"{top_backlog.label}" has the largest open backlog ({int(top_backlog.open)} issues).')

        # Two charts side by side. Each has one series, and the labels are
        # in the same order on both, so the rows line up.
        ordered = table.sort_values('median_days')
        fig, (ax_time, ax_backlog) = plt.subplots(
            1, 2, figsize=(16, max(6, 0.3 * len(ordered))), sharey=True)
        ax_time.barh(ordered['label'], ordered['median_days'], color='tab:blue')
        ax_time.set_title('Median days to close, by label')
        ax_time.set_xlabel('Median days to close')
        ax_time.set_ylabel('Label')
        ax_backlog.barh(ordered['label'], ordered['open'], color='tab:orange')
        ax_backlog.set_title('Open backlog, by label')
        ax_backlog.set_xlabel('Open issues')
        fig.suptitle('Label resolution time and open backlog '
                     f'(labels with at least {MIN_CLOSED_FOR_COMPARISON} closed issues)')
        fig.tight_layout()
        plt.show()

    def _analyze_one_label(self, issues: List[Issue], label: str):
        """
        Single-label view: resolution statistics, the oldest open issues,
        and a histogram of time to close.
        """
        subset = issues_with_label(issues, label)
        if not subset:
            print(f'No issues have the label "{label}".')
            suggestions = difflib.get_close_matches(label, all_labels(issues), n=5, cutoff=0.4)
            if suggestions:
                print('Closest matching labels: ' + ', '.join(suggestions))
            return

        days = [d for d in (resolution_days(i) for i in subset) if d is not None]
        days_series = pd.Series(days, dtype=float)
        open_issues = [i for i in subset if i.state == State.open]

        print(f'Label "{label}": {len(subset)} issues, {len(days)} closed, '
              f'{len(open_issues)} open\n')

        if days:
            within_week = 100 * (days_series <= 7).mean()
            print(f'Median days to close: {days_series.median():.1f}')
            print(f'Mean days to close: {days_series.mean():.1f}')
            print(f'90th percentile days to close: {days_series.quantile(0.9):.1f}')
            print(f'Closed within a week: {within_week:.1f}%')
        else:
            print('No closed issues with a close event, so there are no resolution times.')

        oldest = sorted((i for i in open_issues if i.created_date is not None),
                        key=lambda i: i.created_date)[:TOP_N]
        if oldest:
            print(f'\nOldest {len(oldest)} open issues:')
            for issue in oldest:
                print(f'  #{issue.number} (created {issue.created_date:%Y-%m-%d}) {issue.title}')

        if days:
            # Count closed issues in each time-to-close bucket
            bucket_names = [name for _, name in TIME_BUCKETS]
            bucket_counts = []
            lower = float('-inf')
            for upper, _ in TIME_BUCKETS:
                bucket_counts.append(int(((days_series > lower) & (days_series <= upper)).sum()))
                lower = upper

            print('\nClosed issues by time to close:')
            for name, count in zip(bucket_names, bucket_counts):
                print(f'  {name}: {count}')

            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(bucket_names, bucket_counts, color='tab:green')
            ax.bar_label(bars)
            ax.set_title(f'Time to close for issues labeled "{label}"')
            ax.set_xlabel('Time from creation to close')
            ax.set_ylabel('Number of closed issues')
            fig.tight_layout()

            median = days_series.median()
            within_week = 100 * (days_series <= 7).mean()
            finding = (f'\nFINDING: Half of "{label}" issues close within {median:.1f} days, '
                       f'and {within_week:.0f}% close within a week. '
                       f'{len(open_issues)} are still open')
            if oldest:
                finding += f', the oldest created {oldest[0].created_date:%Y-%m-%d}.'
            else:
                finding += '.'
            print(finding)
            plt.show()


if __name__ == '__main__':
    # Invoke run method when running this module directly
    LabelResolutionAnalysis().run()