from collections import Counter
from typing import List

import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import Issue


class IssueTrendAnalysis:
    """
    Provides overall issue trends and summary statistics.
    """

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        if not issues:
            print('No issues found in dataset.')
            return

        state_counter = Counter(issue.state.value for issue in issues if issue.state)
        label_counter = Counter()
        monthly_counter = Counter()
        event_count_per_issue = []

        for issue in issues:
            for label in issue.labels:
                label_counter[label] += 1

            if issue.created_date is not None:
                month_key = issue.created_date.strftime('%Y-%m')
                monthly_counter[month_key] += 1

            event_count_per_issue.append(len(issue.events))

        avg_events = sum(event_count_per_issue) / len(event_count_per_issue)

        print('\nOverall Issue Trends')
        print('--------------------')
        print(f'Total issues: {len(issues)}')
        print(f'Open issues: {state_counter.get("open", 0)}')
        print(f'Closed issues: {state_counter.get("closed", 0)}')
        print(f'Average events per issue: {avg_events:.2f}\n')

        print('Top labels:')
        for label, count in label_counter.most_common(10):
            print(f'  {label}: {count}')

        print('\nTop months by issue creation:')
        for month, count in monthly_counter.most_common(10):
            print(f'  {month}: {count}')

        top_labels = label_counter.most_common(10)
        if top_labels:
            names = [item[0] for item in top_labels]
            values = [item[1] for item in top_labels]

            plt.figure(figsize=(12, 6))
            plt.bar(names, values)
            plt.title('Top 10 Labels Across All Issues')
            plt.xlabel('Label')
            plt.ylabel('Number of Issues')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
