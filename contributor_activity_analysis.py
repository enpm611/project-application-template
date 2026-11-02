"""
Feature 2: Contributor Activity Analysis

Answers: who does the work in the Poetry issue tracker (opening issues,
commenting, labeling, closing), and what does one contributor's activity
look like over time?

Usage:
    python run.py --feature 2                    # top contributors per activity
    python run.py --feature 2 --user finswimmer  # profile of one contributor
"""

import difflib
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

import config
from data_loader import DataLoader
from model import Issue


# Event types (from the issue timelines) mapped to readable activity names
ACTIVITIES = {
    'opened': 'Issues opened',
    'commented': 'Comments',
    'labeled': 'Labels applied',
    'closed': 'Issues closed',
}
QUESTION = 'Who does the work in the issue tracker (opening, commenting, labeling, closing), and how concentrated is it?'
METHOD = ('Issue creators and the authors of commented, labeled and closed events are counted per person. '
          'Bots and deleted accounts are excluded from rankings.')

# Number of contributors listed per activity
TOP_N: int = 10


def is_bot(user: str) -> bool:
    """
    Accounts that are not real people: automated accounts such as
    github-actions[bot] or stale[bot], and 'ghost', the placeholder
    GitHub shows for deleted accounts.
    """
    return user.endswith('[bot]') or user == 'ghost'



class ContributorActivityAnalysis:
    """
    Counts each contributor's activities across all issues and
    reports the most active contributors or a single user's profile.
    """

    def __init__(self):
        # Parameter is passed in via command line (--user)
        self.USER: Optional[str] = config.get_parameter('user')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()
        df = self.build_dataframe(issues)
        print(f'\nQuestion: {QUESTION}\nMethod:   {METHOD}')

        if df.empty:
            print('No contributor activity found in the data.')
            return

        if self.USER is None:
            self.top_contributors(df)
        else:
            self.user_profile(df, self.USER)

    # ------------------------------------------------------------------ data

    @staticmethod
    def build_dataframe(issues: List[Issue]) -> pd.DataFrame:
        """One row per activity: who did it, what, and when."""
        rows = []
        for issue in issues:
            if issue.creator and issue.created_date is not None:
                rows.append({'user': issue.creator, 'activity': ACTIVITIES['opened'],
                             'date': issue.created_date, 'issue': issue.number})
            for event in issue.events:
                if event.event_type in ACTIVITIES and event.author and event.event_date is not None:
                    rows.append({'user': event.author, 'activity': ACTIVITIES[event.event_type],
                                 'date': event.event_date, 'issue': issue.number})
        df = pd.DataFrame(rows, columns=['user', 'activity', 'date', 'issue'])
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], utc=True)
        return df

    # ------------------------------------------------------ all contributors

    def top_contributors(self, df: pd.DataFrame):
        bots = df['user'].map(is_bot)
        bot_names = sorted(df.loc[bots, 'user'].unique())
        df = df[~bots]
        counts = df.pivot_table(index='user', columns='activity', values='issue',
                                aggfunc='count', fill_value=0)
        counts = counts.reindex(columns=list(ACTIVITIES.values()), fill_value=0)
        counts['Total'] = counts.sum(axis=1)

        print(f'\n\nCONTRIBUTOR ACTIVITY ANALYSIS ({len(counts)} human contributors)\n')
        if bot_names:
            print(f'Excluded {int(bots.sum())} activities by bots and deleted accounts: {", ".join(bot_names)}\n')
        print(f'Top {TOP_N} contributors by total activity:')
        print(counts.sort_values('Total', ascending=False).head(TOP_N).to_string())

        print()
        for activity in ACTIVITIES.values():
            column = counts[activity]
            total = column.sum()
            if total == 0:
                continue
            top5_share = 100 * column.nlargest(5).sum() / total
            active = int((column > 0).sum())
            print(f'{activity:<15} total {total:>6}   by {active:>5} people   '
                  f'top 5 people account for {top5_share:5.1f}%')

        maintainers = counts[ACTIVITIES['closed']].nlargest(5)
        print(f'\nFinding: issue triage is concentrated. The top 5 closers '
              f'({", ".join(maintainers.index)}) closed '
              f'{100 * maintainers.sum() / max(counts[ACTIVITIES["closed"]].sum(), 1):.1f}% of all issues, '
              f'while most of the {len(counts)} contributors only open or comment on issues.\n')

        # Chart: top contributors for each activity
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        for ax, activity in zip(axes.flat, ACTIVITIES.values()):
            top = counts[activity].nlargest(TOP_N).iloc[::-1]
            ax.barh(top.index, top.values, color='steelblue')
            ax.set_title(f'Top {TOP_N}: {activity}')
            ax.set_xlabel('Count')
        fig.suptitle('Poetry issues: most active contributors per activity')
        fig.tight_layout()
        plt.show()

    # ------------------------------------------------------- single user

    def user_profile(self, df: pd.DataFrame, user: str):
        user_df = df[df['user'] == user]
        if user_df.empty:
            users = list(df['user'].unique())
            similar = difflib.get_close_matches(user, users, n=5, cutoff=0.6)
            similar += sorted(u for u in users if user.lower() in u.lower() and u not in similar)
            print(f'\nNo activity found for user "{user}".')
            if similar:
                print('Did you mean: ' + ', '.join(similar[:15]))
            print()
            return

        counts = df.groupby(['activity', 'user']).size()
        print(f'\n\nCONTRIBUTOR ACTIVITY for "{user}"\n')
        print(f'Active from {user_df["date"].min():%Y-%m-%d} to {user_df["date"].max():%Y-%m-%d} '
              f'on {user_df["issue"].nunique()} different issues\n')
        for activity in ACTIVITIES.values():
            if activity not in counts.index.get_level_values(0):
                continue
            per_user = counts[activity]
            mine = int(per_user.get(user, 0))
            if mine:
                rank = int((per_user > mine).sum()) + 1
                print(f'{activity:<15} {mine:>6}   rank {rank} of {len(per_user)} contributors')
            else:
                print(f'{activity:<15} {mine:>6}')

        # Chart: activity per year, stacked by activity type
        per_year = (user_df.assign(year=user_df['date'].dt.year)
                    .pivot_table(index='year', columns='activity', values='issue',
                                 aggfunc='count', fill_value=0))
        per_year = per_year.reindex(columns=[a for a in ACTIVITIES.values() if a in per_year.columns])
        busiest = per_year.sum(axis=1).idxmax()
        print(f'\nFinding: "{user}" was most active in {busiest} '
              f'({int(per_year.sum(axis=1).max())} activities).\n')

        ax = per_year.plot(kind='bar', stacked=True, figsize=(12, 7),
                           title=f'Activity of "{user}" per year', rot=0)
        ax.set_xlabel('Year')
        ax.set_ylabel('# of activities')
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    # Invoke run method when running this module directly
    ContributorActivityAnalysis().run()
