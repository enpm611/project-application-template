"""
state_analysis.py

Analyze Poetry GitHub issues, count total, and by state and display results in
the console.

Usage:
    python states_analysis.py
"""
from typing import List

from data_loader import DataLoader
from model import Issue
from collections import defaultdict

class StateAnalysis:
    """
    Implements an analysis of GitHub issues by stateand outputs the result of
    to the console as plain text.
    """
    def run(self):
        """
        Starting point for the state analysis.

        Run this method to begin analyzing issue states and display the
        results in the console.
        """
        # Load issues from the data file
        issues:List[Issue] = DataLoader().get_issues()

        # Count the number of open and closed issues
        state_count = defaultdict(int)
        for issue in issues:
            state_count[issue.state] += 1

        # Print results
        output = f'Found {len(issues)} issues with the following state counts: \n'
        for state, count in state_count.items():
            output += f'\t{state}: {count}\n'
        print(output)
        
        # For each users, count how many issues are opened
        user_state_count = defaultdict(lambda: defaultdict(int))
        for issue in issues:
            if issue.creator and issue.state == 'open':  # Skip if no creator (optional safeguard)
                user_state_count[issue.creator]['open'] += 1
        
        output = f'Open issue counts per user ({len(user_state_count)} users with open issues):\n:'
        for creator, states in user_state_count.items():
            open_count = states.get('open', 0)
            output += f'{creator}: {open_count}\n'
        print(output)

if __name__ == '__main__':
    # Invoke run method to start analyizing issue states and display results
    # in the console.
    StateAnalysis().run()