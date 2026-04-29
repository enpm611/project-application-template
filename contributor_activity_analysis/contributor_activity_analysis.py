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

    def __init__(self):
        self.USER = config.get_parameter('user')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        if self.USER:
            created_issues = [issue for issue in issues if issue.creator == self.USER]
            matching_events = [
                event
                for issue in issues
                for event in issue.events
                if event.author == self.USER
            ]

            if not created_issues and not matching_events:
                print(f'No activity found for user: {self.USER}')
                return

            print(f'\nContributor: {self.USER}')
            print(f'Issues created: {len(created_issues)}')
            print(f'Events authored: {len(matching_events)}\n')

            event_type_counter = Counter(event.event_type for event in matching_events)

            print('Event type breakdown:')
            for event_type, count in event_type_counter.most_common():
                print(f'  {event_type}: {count}')

            if event_type_counter:
                names = [item[0] for item in event_type_counter.most_common(10)]
                values = [item[1] for item in event_type_counter.most_common(10)]

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
            creator_counter = Counter(issue.creator for issue in issues if issue.creator)
            event_author_counter = Counter(
                event.author
                for issue in issues
                for event in issue.events
                if event.author
            )

            print('\nTop issue creators:')
            for creator, count in creator_counter.most_common(10):
                print(f'  {creator}: {count}')

            print('\nTop event authors:')
            for author, count in event_author_counter.most_common(10):
                print(f'  {author}: {count}')

            top_authors = event_author_counter.most_common(10)
            names = [item[0] for item in top_authors]
            values = [item[1] for item in top_authors]

            plt.figure(figsize=(12, 6))
            plt.bar(names, values)
            plt.title('Top Event Authors Across All Issues')
            plt.xlabel('Contributor')
            plt.ylabel('Number of Events')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
