
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import DataLoader
from model import Issue,Event
import config
from collections import Counter

class analysis_label_types:
    """
    Implements an example analysis of GitHub
    issues and outputs the result of that analysis.
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--months)
        self.months = config.get_parameter('months', default=6)
    
    def run(self):
        """
        Plots number of commits in the last number of months
        """

        issues:List[Issue] = DataLoader().get_issues()

        label_counts = Counter()
        unlabeled_count = 0

        for issue in issues:
            if issue.labels:  # has labels
                label_counts.update(issue.labels)
            else:  # empty list or None
                unlabeled_count += 1

        # Get top 15 labels (excluding unlabeled for now)
        top_labels = label_counts.most_common(15)

        labels, counts = zip(*top_labels) if top_labels else ([], [])

        # Add unlabeled as its own category
        labels = list(labels) + ["unlabeled"]
        counts = list(counts) + [unlabeled_count]

        # Plot
        plt.figure(figsize=(10, 6))
        plt.barh(labels, counts)
        plt.gca().invert_yaxis()

        plt.title("Top 15 Labels + Unlabeled Issues")
        plt.xlabel("Count")

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    # Invoke run method when running this module directly
    analysis_label_types().run()