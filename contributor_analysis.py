from typing import List, Dict, Counter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

from data_loader import DataLoader
from model import Issue, Event
import config

class ContributorAnalysis:
    """
    Implements an analysis of GitHub contributor activity.
    This analysis focuses on:
    1. Top contributors by different metrics
    2. Contributor activity patterns
    3. Contributor focus areas (labels)
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--user)
        self.user: str = config.get_parameter('user')
    
    def run(self):
        """
        Starting point for this analysis.
        """
        issues: List[Issue] = DataLoader().get_issues()
        
        # If a specific user is specified, focus on that user
        if self.user:
            print(f"\n\nAnalyzing activity for contributor: {self.user}\n")
            self._analyze_specific_contributor(issues, self.user)
        else:
            print(f"\n\nAnalyzing contributor activity across all {len(issues)} issues\n")
            self._analyze_all_contributors(issues)
    
    def _analyze_all_contributors(self, issues: List[Issue]):
        """
        Analyzes activity patterns across all contributors
        """
        print("=== Contributor Activity Analysis ===")
        
        # Analyze top issue creators
        # self._analyze_top_issue_creators(issues)
        
        # Analyze top commenters
        # self._analyze_top_commenters(issues)
        
        # Analyze top issue closers
        # self._analyze_top_issue_closers(issues)
        
        # Analyze contributor label focus
        # self._analyze_contributor_label_focus(issues)

if __name__ == '__main__':
    # Invoke run method when running this module directly
    ContributorAnalysis().run()
