"""
Label Resolution Time Controller
Orchestrates the workflow for label resolution analysis and prediction
"""

import json
from datetime import datetime
from pathlib import Path
from analysis.label_resolution_analyzer import LabelResolutionAnalyzer
from model import LabelResolutionPredictor
from typing import Dict, List


class LabelResolutionController:
    """
    Controller for managing label resolution time analysis and predictions
    """
    
    def __init__(self, issues):
        """
        Initialize controller with issues data
        
        Args:
            issues: List of Issue objects
        """
        self.issues = issues
        self.analyzer = LabelResolutionAnalyzer(issues)
        self.predictor = LabelResolutionPredictor()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def run_full_analysis(self) -> Dict:
        """
        Run complete analysis workflow:
        1. Analyze closed issues
        2. Train ML model
        3. Generate predictions for open issues
        4. Create visualizations
        
        Returns:
            Dictionary with all results
        """
        print("=" * 60)
        print("LABEL RESOLUTION TIME ANALYSIS")
        print("=" * 60)
        
        # Step 1: Analyze closed issues
        print("\n[1/4] Analyzing closed issues...")
        label_stats = self.analyzer.analyze_closed_issues()
        summary = self.analyzer.get_summary_statistics()
        
        print(f"  ✓ Analyzed {summary.get('total_closed_issues', 0)} closed issues")
        print(f"  ✓ Found {summary.get('total_unique_labels', 0)} unique labels")
        
        # Step 2: Train ML model
        print("\n[2/4] Training machine learning model...")
        features, labels = self.analyzer.extract_features_for_ml()
        feature_names = self.analyzer.get_feature_names()
        
        training_results = self.predictor.train(features, labels, feature_names)
        
        if training_results['status'] == 'success':
            print(f"  ✓ Model trained on {training_results['training_samples']} samples")
            print(f"  ✓ Model accuracy (R²): {training_results['ensemble']['r2_score']:.3f}")
            print(f"  ✓ Mean error: {training_results['ensemble']['mae_days']:.2f} days")
        else:
            print(f"  ✗ Training failed: {training_results.get('message', 'Unknown error')}")
        
        # Step 3: Generate predictions for open issues
        print("\n[3/4] Generating predictions for open issues...")
        open_predictions = self._predict_open_issues()
        print(f"  ✓ Generated predictions for {len(open_predictions)} open issues")
        
        # Step 4: Save results
        print("\n[4/4] Saving results...")
        results = {
            'analysis_date': datetime.now().isoformat(),
            'summary_statistics': summary,
            'label_statistics': label_stats,
            'model_performance': training_results,
            'open_issue_predictions': open_predictions
        }
        
        self._save_results(results)
        print(f"  ✓ Results saved to {self.output_dir}")
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _predict_open_issues(self) -> List[Dict]:
        """
        Generate predictions for all open issues
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        
        for issue in self.issues:
            # Check if issue is open (works with both objects and dicts)
            state = self.analyzer._get_issue_attr(issue, 'state')
            if state != 'open':
                continue
            
            # Extract issue data
            labels = self.analyzer._get_labels(issue)
            created_at = self.analyzer._get_issue_attr(issue, 'created_date') or self.analyzer._get_issue_attr(issue, 'created_at')
            number = self.analyzer._get_issue_attr(issue, 'number')
            title = self.analyzer._get_issue_attr(issue, 'title') or ''
            
            # Extract features
            issue_data = {
                'issue_number': number,
                'labels': labels,
                'created_at': created_at,
                'closed_at': None
            }
            
            features = self.analyzer._extract_feature_vector(issue_data)
            prediction = self.predictor.predict(features)
            
            if prediction['status'] == 'success':
                predictions.append({
                    'issue_number': number,
                    'title': title[:80],  # Truncate long titles
                    'labels': labels,
                    'predicted_resolution_days': round(prediction['predicted_days'], 2),
                    'confidence_interval': {
                        'lower': round(prediction['confidence_interval']['lower_days'], 2),
                        'upper': round(prediction['confidence_interval']['upper_days'], 2)
                    },
                    'created_at': str(created_at)
                })
        
        # Sort by predicted resolution time
        predictions.sort(key=lambda x: x['predicted_resolution_days'])
        
        return predictions
    
    def query_label_resolution_time(self, label_name: str) -> Dict:
        """
        Query resolution time for a specific label
        
        Args:
            label_name: Name of the label to query
            
        Returns:
            Dictionary with prediction information
        """
        if not self.analyzer.label_stats:
            self.analyzer.analyze_closed_issues()
        
        return self.analyzer.get_label_prediction_time(label_name)
    
    def _save_results(self, results: Dict):
        """
        Save results to JSON files
        
        Args:
            results: Results dictionary
        """
        # Save main results
        output_file = self.output_dir / "label_resolution_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save label statistics separately for easy access
        label_stats_file = self.output_dir / "label_statistics.json"
        with open(label_stats_file, 'w') as f:
            json.dump(results['label_statistics'], f, indent=2, default=str)
        
        # Save predictions separately
        predictions_file = self.output_dir / "open_issue_predictions.json"
        with open(predictions_file, 'w') as f:
            json.dump(results['open_issue_predictions'], f, indent=2, default=str)
    
    def _print_summary(self, results: Dict):
        """
        Print analysis summary to console
        
        Args:
            results: Results dictionary
        """
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        
        summary = results['summary_statistics']
        print(f"\nOverall Statistics:")
        print(f"  • Total closed issues analyzed: {summary.get('total_closed_issues', 0)}")
        print(f"  • Unique labels found: {summary.get('total_unique_labels', 0)}")
        print(f"  • Overall median resolution: {summary.get('overall_median_days', 0):.2f} days")
        print(f"  • Overall average resolution: {summary.get('overall_mean_days', 0):.2f} days")
        
        # Top 10 fastest resolving labels
        print("\n📊 Top 10 Fastest Resolving Labels:")
        label_stats = results['label_statistics']
        sorted_labels = sorted(
            label_stats.items(),
            key=lambda x: x[1]['median_days']
        )[:10]
        
        for i, (label, stats) in enumerate(sorted_labels, 1):
            print(f"  {i:2d}. {label:30s} - {stats['median_days']:6.2f} days (n={stats['count']})")
        
        # Top 10 slowest resolving labels
        print("\n⏰ Top 10 Slowest Resolving Labels:")
        slowest_labels = sorted(
            label_stats.items(),
            key=lambda x: x[1]['median_days'],
            reverse=True
        )[:10]
        
        for i, (label, stats) in enumerate(slowest_labels, 1):
            print(f"  {i:2d}. {label:30s} - {stats['median_days']:6.2f} days (n={stats['count']})")
        
        # Model performance
        if results['model_performance']['status'] == 'success':
            print("\n🤖 Machine Learning Model Performance:")
            metrics = results['model_performance']['ensemble']
            print(f"  • Mean Absolute Error: {metrics['mae_days']:.2f} days")
            print(f"  • R² Score: {metrics['r2_score']:.3f}")
            
            print("\n  Top Feature Importances:")
            feature_imp = results['model_performance']['feature_importance']
            for i, (feature, importance) in enumerate(list(feature_imp.items())[:5], 1):
                print(f"    {i}. {feature}: {importance:.3f}")
        
        # Sample predictions for open issues
        predictions = results['open_issue_predictions']
        if predictions:
            print(f"\n🔮 Sample Predictions for Open Issues (showing 5 of {len(predictions)}):")
            for pred in predictions[:5]:
                labels_str = ', '.join(pred['labels'][:3]) if pred['labels'] else 'No labels'
                print(f"  • Issue #{pred['issue_number']}: {pred['predicted_resolution_days']:.1f} days")
                print(f"    Labels: {labels_str}")
        
        print("\n" + "=" * 60)