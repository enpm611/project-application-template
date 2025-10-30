"""
Label Resolution Time Visualizer
Generates insightful visualizations for label resolution analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List
import pandas as pd


class LabelResolutionVisualizer:
    """
    Creates visualizations for label resolution time analysis
    """
    
    def __init__(self, results: Dict):
        """
        Initialize visualizer with analysis results
        
        Args:
            results: Dictionary containing analysis results
        """
        self.results = results
        self.output_dir = Path("output/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def generate_all_visualizations(self):
        """Generate all visualization types"""
        print("\n[Visualization] Generating graphs...")
        
        self.plot_label_resolution_comparison()
        self.plot_resolution_time_distribution()
        self.plot_feature_importance()
        self.plot_prediction_accuracy()
        self.plot_label_category_analysis()
        self.plot_temporal_trends()
        self.plot_top_labels_comparison()
        
        print(f"  ✓ Visualizations saved to {self.output_dir}")
    
    def plot_label_resolution_comparison(self):
        """
        Plot comparison of resolution times across different labels
        """
        label_stats = self.results['label_statistics']
        
        # Filter labels with sufficient data
        filtered_labels = {
            k: v for k, v in label_stats.items() 
            if v['count'] >= 5
        }
        
        # Sort by median resolution time
        sorted_labels = sorted(
            filtered_labels.items(),
            key=lambda x: x[1]['median_days']
        )[:20]  # Top 20 labels
        
        labels = [item[0] for item in sorted_labels]
        medians = [item[1]['median_days'] for item in sorted_labels]
        means = [item[1]['mean_days'] for item in sorted_labels]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(labels))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, medians, width, label='Median', color='#3498db')
        bars2 = ax.barh(x + width/2, means, width, label='Mean', color='#e74c3c')
        
        ax.set_ylabel('Label')
        ax.set_xlabel('Resolution Time (days)')
        ax.set_title('Label Resolution Time Comparison\n(Top 20 Fastest Resolving Labels)', 
                     fontsize=14, fontweight='bold')
        ax.set_yticks(x)
        ax.set_yticklabels(labels, fontsize=9)
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'label_resolution_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_resolution_time_distribution(self):
        """
        Plot distribution of resolution times
        """
        label_stats = self.results['label_statistics']
        
        # Collect all median times
        median_times = [stats['median_days'] for stats in label_stats.values()]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Histogram
        ax1.hist(median_times, bins=30, color='#3498db', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Median Resolution Time (days)')
        ax1.set_ylabel('Number of Labels')
        ax1.set_title('Distribution of Label Resolution Times', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Box plot
        ax2.boxplot(median_times, vert=True, patch_artist=True,
                    boxprops=dict(facecolor='#3498db', alpha=0.7),
                    medianprops=dict(color='red', linewidth=2))
        ax2.set_ylabel('Median Resolution Time (days)')
        ax2.set_title('Box Plot of Resolution Times', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'resolution_time_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_feature_importance(self):
        """
        Plot feature importance from ML model
        """
        if self.results['model_performance']['status'] != 'success':
            return
        
        feature_imp = self.results['model_performance']['feature_importance']
        
        features = list(feature_imp.keys())
        importance = list(feature_imp.values())
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = sns.color_palette('viridis', len(features))
        bars = ax.barh(features, importance, color=colors)
        
        ax.set_xlabel('Importance Score')
        ax.set_title('Feature Importance for Resolution Time Prediction', 
                     fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{width:.3f}',
                   ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'feature_importance.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_prediction_accuracy(self):
        """
        Plot model prediction accuracy metrics
        """
        if self.results['model_performance']['status'] != 'success':
            return
        
        metrics = self.results['model_performance']
        
        models = ['Random Forest', 'Gradient Boosting', 'Ensemble']
        mae_values = [
            metrics['random_forest']['mae_days'],
            metrics['gradient_boosting']['mae_days'],
            metrics['ensemble']['mae_days']
        ]
        r2_values = [
            metrics['random_forest']['r2_score'],
            metrics['gradient_boosting']['r2_score'],
            metrics['ensemble']['r2_score']
        ]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # MAE comparison
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        ax1.bar(models, mae_values, color=colors, alpha=0.7)
        ax1.set_ylabel('Mean Absolute Error (days)')
        ax1.set_title('Model Prediction Error Comparison', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(mae_values):
            ax1.text(i, v, f'{v:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # R² Score comparison
        ax2.bar(models, r2_values, color=colors, alpha=0.7)
        ax2.set_ylabel('R² Score')
        ax2.set_title('Model Accuracy (R² Score)', fontsize=12, fontweight='bold')
        ax2.set_ylim([0, 1])
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(r2_values):
            ax2.text(i, v, f'{v:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'prediction_accuracy.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_label_category_analysis(self):
        """
        Analyze resolution times by label categories (bug, feature, docs, etc.)
        """
        label_stats = self.results['label_statistics']
        
        categories = {
            'Bug': [],
            'Feature/Enhancement': [],
            'Documentation': [],
            'Area': [],
            'Other': []
        }
        
        for label, stats in label_stats.items():
            label_lower = label.lower()
            if 'bug' in label_lower:
                categories['Bug'].append(stats['median_days'])
            elif 'feature' in label_lower or 'enhancement' in label_lower:
                categories['Feature/Enhancement'].append(stats['median_days'])
            elif 'doc' in label_lower:
                categories['Documentation'].append(stats['median_days'])
            elif 'area/' in label_lower:
                categories['Area'].append(stats['median_days'])
            else:
                categories['Other'].append(stats['median_days'])
        
        # Filter out empty categories
        categories = {k: v for k, v in categories.items() if v}
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        data = list(categories.values())
        labels = list(categories.keys())
        
        bp = ax.boxplot(data, labels=labels, patch_artist=True,
                        medianprops=dict(color='red', linewidth=2))
        
        # Color boxes
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Median Resolution Time (days)', fontsize=12)
        ax.set_title('Resolution Time by Label Category', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'label_category_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_temporal_trends(self):
        """
        Plot temporal trends in resolution times (if data available)
        """
        # This would require temporal data from the analyzer
        # Placeholder for future implementation
        pass
    
    def plot_top_labels_comparison(self):
        """
        Create a detailed comparison of top labels
        """
        label_stats = self.results['label_statistics']
        
        # Get top 15 labels by count
        top_labels = sorted(
            label_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:15]
        
        labels = [item[0] for item in top_labels]
        counts = [item[1]['count'] for item in top_labels]
        medians = [item[1]['median_days'] for item in top_labels]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Issue count
        bars1 = ax1.barh(labels, counts, color='#3498db', alpha=0.7)
        ax1.set_xlabel('Number of Issues')
        ax1.set_title('Top 15 Labels by Issue Count', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars1:
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}',
                    ha='left', va='center', fontsize=9)
        
        # Resolution time
        bars2 = ax2.barh(labels, medians, color='#e74c3c', alpha=0.7)
        ax2.set_xlabel('Median Resolution Time (days)')
        ax2.set_title('Median Resolution Time for Top Labels', fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar in bars2:
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}',
                    ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'top_labels_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()