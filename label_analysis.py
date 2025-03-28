from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from data_loader import DataLoader
from model import Issue, Event, State
import config

class LabelAnalysis:
    """
    Implements an analysis of GitHub issues based on labels.
    This analysis focuses on:
    1. Label distribution across issues
    2. Activity level of issues with specific labels
    3. Resolution time for issues with specific labels
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--label)
        self.label: str = config.get_parameter('label')
    
    def run(self):
        """
        Starting point for this analysis.
        """
        issues: List[Issue] = DataLoader().get_issues()
        
        # Filter issues by label if specified
        if self.label:
            filtered_issues = [issue for issue in issues if self.label in issue.labels]
            print(f"\n\nAnalyzing {len(filtered_issues)} issues with label '{self.label}'\n")
        else:
            filtered_issues = issues
            print(f"\n\nAnalyzing label distribution across all {len(issues)} issues\n")
        
        # Analyze label distribution
        # self._analyze_label_distribution(issues)
        
        # Analyze label activity (comments per issue)
        # self._analyze_label_activity(issues)
        
        # Analyze resolution time by label
        # self._analyze_resolution_time(issues)

if __name__ == '__main__':
    # Invoke run method when running this module directly
    LabelAnalysis().run()
