from config import ConfigManager
from controllers.contributors_controller import ContributorsController
from controllers.label_resolution_controller import LabelResolutionController
from visualization.label_resolution_visualizer import LabelResolutionVisualizer
from data_loader import DataLoader
class FeatureRunner:
    def __init__(self):
        self.config = None
        self.contributors_controller = None

    def initialize_components(self):
        # Initialize config and the ContributorsController
        self.config = ConfigManager("config.json")
        self.contributors_controller = ContributorsController()

    def run_feature(self, feature_number: int, user: str = None, label: str = None):
        """
        Dispatch to the appropriate controller based on feature number.
        1 = Lifecycle Analysis
        2 = Contributors Dashboard
        3 = Priority Analysis
        """
        if feature_number == 1:
            data_path = self.config.get_data_path()
            DataLoaderInstance = DataLoader()
            issues = DataLoaderInstance.get_issues()
            print("\n" + "="*70)
            print("FEATURE 1: LABEL RESOLUTION TIME ANALYSIS AND PREDICTION")
            print("="*70)
            
            # Initialize controller
            controller = LabelResolutionController(issues)
            
            # Run full analysis
            results = controller.run_full_analysis()
            
            # Generate visualizations
            visualizer = LabelResolutionVisualizer(results)
            visualizer.generate_all_visualizations()
            
            print("\n" + "="*70)
            print("FEATURE 1 COMPLETED")
            print("="*70)
            print("\nOutput Files:")
            print("  • output/label_resolution_analysis.json - Complete analysis results")
            print("  • output/label_statistics.json - Label-wise statistics")
            print("  • output/open_issue_predictions.json - Predictions for open issues")
            print("  • output/visualizations/ - All generated graphs")
            print("\n" + "="*70)
            
            # Example: Query specific label
            print("\nExample Query:")
            example_labels = ['Area/Docs', 'kind/bug', 'kind/feature']
            for label in example_labels:
                result = controller.query_label_resolution_time(label)
                if result['status'] == 'success':
                    print(f"\n{label}:")
                    print(f"  Expected resolution: {result['predicted_days']} days")
                    print(f"  Based on {result['based_on_issues']} historical issues")
                    print(f"  Confidence range: {result['confidence_range']['min_days']}-"
                        f"{result['confidence_range']['max_days']} days")
                else:
                    print(f"\n{label}: {result['message']}")
                
            print(results)

        elif feature_number == 2:
            print("▶ Running Contributors Dashboard...")
            data_path = self.config.get_data_path()
            output_path = self.config.get_output_path()

            issues_df, events_df = self.contributors_controller.load_contributor_data()
            contributors = self.contributors_controller.analyzer.build_contributors(issues_df, events_df)

            figs = {}
            
            # ---------------- Graph 1: Bug Closure Distribution ----------------
            figs["graph1_bug_closures"] = self.contributors_controller.plot_bug_closure_distribution(
                issues_df, events_df
            )

            # ---------------- Graph 2: Top Feature Requesters ----------------
            fig2 = self.contributors_controller.plot_top_feature_requesters(issues_df, top_n=10)
            if fig2 is not None:
                figs["graph2_top_feature_requesters"] = fig2

            # ---------------- Graph 3: Docs Issues Analysis ----------------
            fig3 = self.contributors_controller.plot_docs_issues(issues_df, events_df)
            if fig3 is not None:
                figs["graph3_docs_issues"] = fig3
                
            # ---------------- Graph 4: Issues Created per User ----------------
            fig4 = self.contributors_controller.plot_issues_created_per_user(issues_df, top_n=40)
            if fig4 is not None:
                figs["graph4_issues_created_per_user"] = fig4
            
            # ---------------- Graph 5: Top Active Users per Year ----------------
            fig5 = self.contributors_controller.plot_top_active_users_per_year(contributors, top_n=10)
            if fig5 is not None:
                # Interactive Plotly figure
                figs["graph5_top_active_users_per_year"] = fig5
                fig5.show()
            
            # ---------------- Graph 6: Engagement Heatmap ----------------
            fig6 = self.contributors_controller.run_engagement_heatmap(contributors)
            if fig6 is not None:
                figs["graph6_engagement_heatmap"] = fig6
            
            # ---------------- Graph 7: Contributor Lifecycle Stages ----------------
            fig7 = self.contributors_controller.run_contributor_lifecycle(contributors)
            if fig7 is not None:
                figs["graph7_contributor_lifecycle"] = fig7
                
            # Saving the figures in output path
            for name, fig in figs.items():
                self.contributors_controller.visualizer.save_figure(fig, f"{output_path}/{name}.png")
                print(f"Saved {name} → {output_path}/{name}.png")

            # Displaying the figures
            import matplotlib.pyplot as plt
            plt.show()


        elif feature_number == 3:
            print("▶ Running Priority Analysis...")
            pass

        else:
            print("❌ Oops, this is an unknown feature number! Use --feature 1, 2, or 3.")