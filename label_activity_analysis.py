from collections import Counter
from typing import List, Optional

import matplotlib.pyplot as plt

import config
from data_loader import DataLoader
from model import Issue



class LabelActivityAnalysis:
    def __init__(self, issues=None):
        self.issues = issues
        try:
            self.LABEL = config.get_parameter("label")
        except Exception:
            self.LABEL = None

    def run(self):
        issues: List[Issue] = (
            self.issues if self.issues is not None else DataLoader().load_data()
        )

        if not issues:
            print("No issues found in dataset.")
            return

        if self.LABEL:
            filtered_issues = [
                issue for issue in issues
                if self.LABEL in (getattr(issue, "labels", []) or [])
            ]
        else:
            filtered_issues = issues

        if not filtered_issues:
            print(f'No issues found for label: {self.LABEL}')
            return

        print(f'\nFound {len(filtered_issues)} matching issues.\n')

        label_counter = Counter()
        event_counter = Counter()

        for issue in filtered_issues:
        
            for label in getattr(issue, "labels", []) or []:
                label_counter[label] += 1

        
            for event in getattr(issue, "events", []) or []:
                event_type = getattr(event, "event_type", None)
                if event_type:
                    event_counter[event_type] += 1

        print('Top labels in filtered issues:')
        for label, count in label_counter.most_common(10):
            print(f'  {label}: {count}')

        print('\nTop event types in filtered issues:')
        for event_type, count in event_counter.most_common(10):
            print(f'  {event_type}: {count}')

   
        if event_counter:
            top_items = event_counter.most_common(10)
            names = [k for k, _ in top_items]
            values = [v for _, v in top_items]

            plt.figure(figsize=(12, 6))
            plt.bar(names, values)
            plt.title(
                f'Event Types for Label: {self.LABEL}'
                if self.LABEL
                else 'Top Event Types Across All Issues'
            )
            plt.xlabel('Event Type')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
