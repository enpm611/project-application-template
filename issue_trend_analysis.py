from collections import Counter
from typing import List, Optional

import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import Issue


class IssueTrendAnalysis:
    def __init__(self, issues: Optional[List[Issue]] = None):
        self.issues = issues

    def run(self):
 
        issues = self.issues or DataLoader().load_data()

        if not issues:
            print('No issues found in dataset.')
            return

        state_counter = Counter(
            getattr(issue.state, "value", None)
            for issue in issues
            if getattr(issue, "state", None)
        )

        label_counter = Counter()
        monthly_counter = Counter()
        event_count_per_issue = []

        for issue in issues:
            
            for label in getattr(issue, "labels", []) or []:
                label_counter[label] += 1

        
            created_date = getattr(issue, "created_date", None)
            if created_date:
                try:
                    month_key = created_date.strftime('%Y-%m')
                    monthly_counter[month_key] += 1
                except Exception:
                    pass

            events = getattr(issue, "events", []) or []
            event_count_per_issue.append(len(events))

        
        avg_events = (
            sum(event_count_per_issue) / len(event_count_per_issue)
            if event_count_per_issue else 0
        )

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

     
        if label_counter:
            names = [k for k, _ in label_counter.most_common(10)]
            values = [v for _, v in label_counter.most_common(10)]

            plt.figure(figsize=(12, 6))
            plt.bar(names, values)
            plt.title('Top 10 Labels Across All Issues')
            plt.xlabel('Label')
            plt.ylabel('Number of Issues')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
