from collections import Counter
from typing import List

import matplotlib.pyplot as plt

import config
from data_loader import DataLoader
from model import Issue


class ContributorActivityAnalysis:
    """
    Analyzes contributor activity across issues and events.
    Can focus on a specific contributor if --user is provided.
    """

    def __init__(self, issues=None):
        # Always define USER safely
        try:
            self.USER = config.get_parameter('user')
        except Exception:
            self.USER = None

        self.issues = issues

    def run(self):
        
        issues: List[Issue] = self.issues or DataLoader().load_data()

        if not issues:
            print("No issues found in dataset.")
            return

        if self.USER:
            created_issues = [
                issue for issue in issues
                if getattr(issue, "creator", None) == self.USER
            ]

            matching_events = [
                event
                for issue in issues
                for event in getattr(issue, "events", [])
                if getattr(event, "author", None) == self.USER
            ]

            if not created_issues and not matching_events:
                print(f'No activity found for user: {self.USER}')
                return

            print(f'\nContributor: {self.USER}')
            print(f'Issues created: {len(created_issues)}')
            print(f'Events authored: {len(matching_events)}\n')

            event_type_counter = Counter(
                getattr(event, "event_type", None)
                for event in matching_events
                if getattr(event, "event_type", None)
            )

            print('Event type breakdown:')
            for event_type, count in event_type_counter.most_common():
                print(f'  {event_type}: {count}')

            if event_type_counter:
                names = [k for k, _ in event_type_counter.most_common(10)]
                values = [v for _, v in event_type_counter.most_common(10)]

                plt.figure(figsize=(12, 6))
                plt.bar(names, values)
                plt.title(f'Event Types for Contributor: {self.USER}')
                plt.xlabel('Event Type')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
            else:
                print('\nThis user created issues but has no authored events in the dataset.')

        else:
            creator_counter = Counter(
                getattr(issue, "creator", None)
                for issue in issues
                if getattr(issue, "creator", None)
            )

            event_author_counter = Counter(
                getattr(event, "author", None)
                for issue in issues
                for event in getattr(issue, "events", [])
                if getattr(event, "author", None)
            )

            print('\nTop issue creators:')
            for creator, count in creator_counter.most_common(10):
                print(f'  {creator}: {count}')

            print('\nTop event authors:')
            for author, count in event_author_counter.most_common(10):
                print(f'  {author}: {count}')

            if event_author_counter:
                names = [k for k, _ in event_author_counter.most_common(10)]
                values = [v for _, v in event_author_counter.most_common(10)]

                plt.figure(figsize=(12, 6))
                plt.bar(names, values)
                plt.title('Top Event Authors Across All Issues')
                plt.xlabel('Contributor')
                plt.ylabel('Number of Events')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
