from typing import List

import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue, State
import config


class IssueTrendAnalysis:
    def __init__(self):
        # Comes from the --label command-line argument
        self.label = config.get_parameter('label')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        # If --label was provided, focus on issues with that label
        if self.label is not None:
            issues = [issue for issue in issues if self.label in issue.labels]

        chart_label = f' for "{self.label}"' if self.label is not None else ''

        print(f'Found {len(issues)} issues')
        if self.label is not None:
            print(f'with the "{self.label}" label')

        # Build quarterly opened and closed counts from issue dates and events.
        quarterly_events = []
        fallback_close_dates = 0
        for issue in issues:
            if issue.created_date is not None:
                quarterly_events.append({
                    'date': issue.created_date,
                    'event': 'opened'
                })

            has_closed_event = False
            for event in issue.events:
                if (
                    event.event_type is not None
                    and event.event_type.lower() == 'closed'
                ):
                    has_closed_event = True
                    if event.event_date is not None:
                        quarterly_events.append({
                            'date': event.event_date,
                            'event': 'closed'
                        })

            if (
                issue.state == State.closed
                and not has_closed_event
                and issue.updated_date is not None
            ):
                quarterly_events.append({
                    'date': issue.updated_date,
                    'event': 'closed'
                })
                fallback_close_dates += 1

        quarterly_df = pd.DataFrame.from_records(
            quarterly_events,
            columns=['date', 'event']
        )
        if quarterly_df.empty:
            print('No issue creation or closure dates available for the quarterly time series.')
        else:
            quarterly_df['quarter'] = pd.to_datetime(
                quarterly_df['date'],
                utc=True
            ).dt.to_period('Q')
            quarterly_counts = (
                quarterly_df.groupby(['quarter', 'event'])
                .size()
                .unstack(fill_value=0)
                .reindex(columns=['opened', 'closed'], fill_value=0)
            )
            all_quarters = pd.period_range(
                start=quarterly_counts.index.min(),
                end=quarterly_counts.index.max(),
                freq='Q'
            )
            quarterly_counts = quarterly_counts.reindex(all_quarters, fill_value=0)
            quarterly_counts['backlog'] = (
                quarterly_counts['opened'] - quarterly_counts['closed']
            ).cumsum()

            print('\nQuarterly issue activity and end-of-quarter backlog:')
            print(quarterly_counts.to_string())
            print(
                'Backlog is cumulative from the first quarter in the data, '
                'assuming zero issues were already open before then.'
            )
            if fallback_close_dates:
                print(
                    f'Used last updated date as the close date for '
                    f'{fallback_close_dates} closed issue(s) without a '
                    f'closed event.'
                )

            total_opened = int(quarterly_counts['opened'].sum())
            total_closed = int(quarterly_counts['closed'].sum())
            print(f'\nTotal issues opened: {total_opened}')
            print(f'Total issues closed: {total_closed}')

            activity = quarterly_counts['opened'] + quarterly_counts['closed']

            def format_quarters(quarters):
                return ', '.join(str(quarter) for quarter in quarters)

            busiest_quarters = activity[activity == activity.max()].index
            busiest_open_quarters = quarterly_counts[
                quarterly_counts['opened'] == quarterly_counts['opened'].max()
            ].index
            busiest_closed_quarters = quarterly_counts[
                quarterly_counts['closed'] == quarterly_counts['closed'].max()
            ].index
            print(
                f'Busiest quarter(s) by combined activity: '
                f'{format_quarters(busiest_quarters)} '
                f'({int(activity.max())} events)'
            )
            print(
                f'Most issues opened in: {format_quarters(busiest_open_quarters)} '
                f'({int(quarterly_counts["opened"].max())})'
            )
            print(
                f'Most issues closed in: {format_quarters(busiest_closed_quarters)} '
                f'({int(quarterly_counts["closed"].max())})'
            )

            peak_backlog_quarter = quarterly_counts['backlog'].idxmax()
            print(
                f'Peak recorded backlog: {int(quarterly_counts["backlog"].max())} '
                f'at the end of {peak_backlog_quarter}'
            )

            yearly_summary = quarterly_counts.groupby(
                quarterly_counts.index.year
            ).agg(
                opened=('opened', 'sum'),
                closed=('closed', 'sum'),
                backlog_at_last_quarter=('backlog', 'last')
            )
            yearly_summary.index.name = 'year'
            print(
                '\nPer-year summary (backlog is for the last available '
                'quarter in each year):'
            )
            print(yearly_summary.to_string())

            if len(quarterly_counts) >= 4:
                comparison_quarter = quarterly_counts.index[-4]
                latest_quarter = quarterly_counts.index[-1]
                backlog_change = (
                    quarterly_counts['backlog'].iloc[-1]
                    - quarterly_counts['backlog'].iloc[-4]
                )
                print(
                    f'\nBacklog change over the last 4 quarters '
                    f'({comparison_quarter} to {latest_quarter}): '
                    f'{int(backlog_change):+d}'
                )
            else:
                print(
                    '\nBacklog change over the last 4 quarters: '
                    'not available (fewer than 4 quarterly data points).'
                )
             
                # charts
                
            fig, (activity_ax, backlog_ax) = plt.subplots(
                2,
                1,
                figsize=(14, 10),
                sharex=True
            )
            quarterly_counts[['opened', 'closed']].plot(
                kind='line',
                marker='o',
                ax=activity_ax,
                title=f'Quarterly Issues Opened and Closed{chart_label}'
            )
            activity_ax.set_ylabel('# of issues')
            activity_ax.grid(True, axis='y', alpha=0.3)

            quarterly_counts['backlog'].plot(
                kind='line',
                marker='o',
                ax=backlog_ax,
                color='tab:purple',
                title=f'Backlog of Total Open Issues Per Quarter{chart_label}'
            )
            backlog_ax.set_xlabel('Quarter')
            backlog_ax.set_ylabel('# of open issues')
            backlog_ax.grid(True, axis='y', alpha=0.3)
            fig.tight_layout()

        plt.show()



if __name__ == '__main__':
    # Invoke run method when running this module directly
    IssueTrendAnalysis().run()
