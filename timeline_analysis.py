from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

from data_loader import DataLoader
from model import Issue, Event, State
import config

class TimelineAnalysis:
    """
    Implements an analysis of GitHub issues over time.
    This analysis focuses on:
    1. Issue creation and closing patterns over time
    2. Issue lifecycle (time to first response, time to resolution)
    3. Activity trends over time
    """
    
    def __init__(self):
        """
        Constructor
        """
        # No specific parameters needed for this analysis
        pass
    
    def run(self):
        """
        Starting point for this analysis.
        """
        issues: List[Issue] = DataLoader().get_issues()
        
        print(f"\n\nAnalyzing issue timeline patterns across {len(issues)} issues\n")
        
        # Analyze issue creation and closing over time
        # self._analyze_issue_creation_closing(issues)
        
        # Analyze issue lifecycle
        # self._analyze_issue_lifecycle(issues)
        
        # Analyze activity trends
        # self._analyze_activity_trends(issues)

if __name__ == '__main__':
    # Invoke run method when running this module directly
    TimelineAnalysis().run()
