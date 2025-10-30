"""
Label Resolution Time Analyzer
Analyzes closed issues to determine resolution times for different label types
and extracts features for ML prediction.
"""

from datetime import datetime
from typing import List, Dict, Tuple, Union
from collections import defaultdict
import statistics
from typing import Dict, List, Tuple


class LabelResolutionAnalyzer:
    """Analyzes label resolution times from closed issues"""
    
    def __init__(self, issues):
        """
        Initialize analyzer with issues data
        
        Args:
            issues: List of Issue objects from data model
        """
        self.issues = issues
        self.label_stats = {}
        self.resolution_data = []
        
    def _get_issue_attr(self, issue, attr: str):
        """
        Get attribute from issue (works with both objects and dicts)
        
        Args:
            issue: Issue object or dict
            attr: Attribute name
            
        Returns:
            Attribute value
        """
        if isinstance(issue, dict):
            return issue.get(attr)
        return getattr(issue, attr, None)
    
    def _get_labels(self, issue) -> List[str]:
        """
        Get labels from issue (works with both objects and dicts)
        
        Args:
            issue: Issue object or dict
            
        Returns:
            List of label strings
        """
        if isinstance(issue, dict):
            return issue.get('labels', [])
        
        # Issue object with Label objects
        labels_obj = getattr(issue, 'labels', None)
        if labels_obj is None:
            return []
        
        if isinstance(labels_obj, list):
            if len(labels_obj) > 0 and hasattr(labels_obj[0], 'name'):
                return [label.name for label in labels_obj]
            return labels_obj
        
        return []
        
    def analyze_closed_issues(self) -> Dict:
        """
        Analyze all closed issues to calculate resolution time statistics
        
        Returns:
            Dictionary containing label-wise resolution statistics
        """
        label_times = defaultdict(list)
        
        for issue in self.issues:
            state = self._get_issue_attr(issue, 'state')
            if state != 'closed':
                continue
            
            # Get closed_at date
            closed_at = self._get_closed_date(issue)
            if not closed_at:
                continue
                
            resolution_time = self._calculate_resolution_time(issue, closed_at)
            if resolution_time is None:
                continue
            
            # Get labels
            labels = self._get_labels(issue)
            
            # Store resolution data for ML
            self.resolution_data.append({
                'issue_number': self._get_issue_attr(issue, 'number'),
                'labels': labels,
                'resolution_time_hours': resolution_time,
                'created_at': self._get_issue_attr(issue, 'created_date') or self._get_issue_attr(issue, 'created_at'),
                'closed_at': closed_at
            })
            
            # Group by each label
            if labels:
                for label in labels:
                    label_times[label].append(resolution_time)
            else:
                label_times['no_label'].append(resolution_time)
        
        # Calculate statistics for each label
        self.label_stats = self._calculate_label_statistics(label_times)
        
        return self.label_stats
    
    def _get_closed_date(self, issue) -> str:
        """
        Extract closed date from issue (events or closed_at attribute)
        
        Args:
            issue: Issue object or dict
            
        Returns:
            Closed date string or None
        """
        # Try closed_at attribute first (Issue object)
        closed_at = self._get_issue_attr(issue, 'closed_at')
        if closed_at:
            return closed_at
        
        # Try events array (JSON format)
        events = self._get_issue_attr(issue, 'events')
        if events:
            for event in events:
                if isinstance(event, dict):
                    if event.get('event_type') == 'closed':
                        return event.get('event_date')
                elif hasattr(event, 'event_type'):
                    if event.event_type == 'closed':
                        return event.event_date
        
        return None
    
    def _calculate_resolution_time(self, issue, closed_at: str) -> float:
        """
        Calculate resolution time in hours
        
        Args:
            issue: Issue object or dict
            closed_at: Closed date string
            
        Returns:
            Resolution time in hours or None if cannot be calculated
        """
        try:
            # Get created_at
            created_str = self._get_issue_attr(issue, 'created_date') or self._get_issue_attr(issue, 'created_at')
            
            if isinstance(created_str, str):
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            else:
                created = created_str
            
            if isinstance(closed_at, str):
                closed = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
            else:
                closed = closed_at
            
            delta = closed - created
            return delta.total_seconds() / 3600  # Convert to hours
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            return None
    
    def _calculate_label_statistics(self, label_times: Dict) -> Dict:
        """
        Calculate statistical metrics for each label
        
        Args:
            label_times: Dictionary mapping labels to list of resolution times
            
        Returns:
            Dictionary with statistical metrics per label
        """
        stats = {}
        
        for label, times in label_times.items():
            if not times:
                continue
                
            sorted_times = sorted(times)
            
            stats[label] = {
                'count': len(times),
                'mean_hours': statistics.mean(times),
                'median_hours': statistics.median(times),
                'std_dev_hours': statistics.stdev(times) if len(times) > 1 else 0,
                'min_hours': min(times),
                'max_hours': max(times),
                'percentile_25': sorted_times[len(times) // 4] if len(times) >= 4 else sorted_times[0],
                'percentile_75': sorted_times[3 * len(times) // 4] if len(times) >= 4 else sorted_times[-1],
                'mean_days': statistics.mean(times) / 24,
                'median_days': statistics.median(times) / 24
            }
        
        return stats
    
    def get_label_prediction_time(self, label_name: str) -> Dict:
        """
        Get predicted resolution time for a specific label
        
        Args:
            label_name: Name of the label
            
        Returns:
            Dictionary with prediction information
        """
        if label_name not in self.label_stats:
            return {
                'label': label_name,
                'status': 'unknown',
                'message': f'No historical data found for label: {label_name}'
            }
        
        stats = self.label_stats[label_name]
        
        return {
            'label': label_name,
            'status': 'success',
            'predicted_days': round(stats['median_days'], 2),
            'predicted_hours': round(stats['median_hours'], 2),
            'confidence_range': {
                'min_days': round(stats['percentile_25'] / 24, 2),
                'max_days': round(stats['percentile_75'] / 24, 2)
            },
            'based_on_issues': stats['count'],
            'statistics': {
                'average_days': round(stats['mean_days'], 2),
                'fastest_days': round(stats['min_hours'] / 24, 2),
                'slowest_days': round(stats['max_hours'] / 24, 2)
            }
        }
    
    def extract_features_for_ml(self) -> Tuple[List, List]:
        """
        Extract features and labels for machine learning
        
        Returns:
            Tuple of (features, labels) for ML training
        """
        features = []
        labels = []
        
        for data in self.resolution_data:
            feature_vector = self._extract_feature_vector(data)
            features.append(feature_vector)
            labels.append(data['resolution_time_hours'])
        
        return features, labels
    
    def _extract_feature_vector(self, issue_data: Dict) -> List:
        """
        Extract numerical feature vector from issue data
        
        Args:
            issue_data: Dictionary containing issue information
            
        Returns:
            List of numerical features
        """
        # Feature extraction
        labels = issue_data.get('labels', [])
        num_labels = len(labels)
        
        # Label type features (one-hot-like encoding for common labels)
        has_bug = 1 if any('bug' in str(l).lower() for l in labels) else 0
        has_feature = 1 if any('feature' in str(l).lower() or 'enhancement' in str(l).lower() 
                               for l in labels) else 0
        has_docs = 1 if any('doc' in str(l).lower() for l in labels) else 0
        has_area = 1 if any('area/' in str(l).lower() for l in labels) else 0
        
        # Temporal features (day of week, month)
        try:
            created_str = issue_data.get('created_at')
            if isinstance(created_str, str):
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            else:
                created = created_str
            day_of_week = created.weekday()
            month = created.month
        except:
            day_of_week = 0
            month = 1
        
        return [
            num_labels,
            has_bug,
            has_feature,
            has_docs,
            has_area,
            day_of_week,
            month
        ]
    
    def get_feature_names(self) -> List[str]:
        """
        Get names of features used in ML model
        
        Returns:
            List of feature names
        """
        return [
            'num_labels',
            'has_bug_label',
            'has_feature_label',
            'has_docs_label',
            'has_area_label',
            'day_of_week',
            'month'
        ]
    
    def get_summary_statistics(self) -> Dict:
        """
        Get overall summary statistics across all labels
        
        Returns:
            Dictionary with summary statistics
        """
        all_times = []
        for times in [data['resolution_time_hours'] for data in self.resolution_data]:
            all_times.append(times)
        
        if not all_times:
            return {}
        
        return {
            'total_closed_issues': len(self.resolution_data),
            'total_unique_labels': len(self.label_stats),
            'overall_median_days': round(statistics.median(all_times) / 24, 2),
            'overall_mean_days': round(statistics.mean(all_times) / 24, 2),
            'fastest_resolution_days': round(min(all_times) / 24, 2),
            'slowest_resolution_days': round(max(all_times) / 24, 2)
        }