import os
import matplotlib.pyplot as plt


class GraphGenerator:

    def __init__(self, reports_folder):

        self.reports_folder = reports_folder

    def create_output_folder(self):

        graphs_path = os.path.join(
            self.reports_folder,
            'graphs'
        )

        os.makedirs(graphs_path, exist_ok=True)

        return graphs_path

    # ---------------------------------------------------
    # GRAPH 1
    # ---------------------------------------------------

    def production_summary_graph(self, summary_df):

        graphs_path = self.create_output_folder()

        plt.figure(figsize=(10, 6))

        plt.bar(
            summary_df['EOL'],
            summary_df['Total NOK']
        )

        plt.xlabel('EOL')
        plt.ylabel('Total NOK')
        plt.title('EOL-wise NOK Comparison')

        save_path = os.path.join(
            graphs_path,
            'production_summary.png'
        )

        plt.savefig(save_path)

        plt.close()

        print(f"Saved: {save_path}")

    # ---------------------------------------------------
    # GRAPH 2
    # ---------------------------------------------------

    def failure_rate_graph(self, summary_df):

        graphs_path = self.create_output_folder()

        plt.figure(figsize=(10, 6))

        plt.bar(
            summary_df['EOL'],
            summary_df['Average Failure %']
        )

        plt.xlabel('EOL')
        plt.ylabel('Average Failure %')
        plt.title('Average Failure Percentage')

        save_path = os.path.join(
            graphs_path,
            'failure_rate.png'
        )

        plt.savefig(save_path)

        plt.close()

        print(f"Saved: {save_path}")

    # ---------------------------------------------------
    # GRAPH 3
    # ---------------------------------------------------

    def top_failures_graph(self, root_cause_df):

        graphs_path = self.create_output_folder()

        # Safety check
        if root_cause_df.empty:

            print("root_cause_df is empty")

            return

        print("\nRoot Cause DF Columns:")
        print(root_cause_df.columns)

        # Group data
        top_failures = (
            root_cause_df
            .groupby('Failure')['Count']
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        plt.figure(figsize=(14, 8))

        top_failures.plot(kind='bar')

        plt.xlabel('Failure')
        plt.ylabel('Count')

        plt.title('Top 10 Recurring Failures')

        plt.xticks(rotation=75)

        save_path = os.path.join(
            graphs_path,
            'top_failures.png'
        )

        plt.savefig(
            save_path,
            bbox_inches='tight'
        )

        plt.close()

        print(f"Saved: {save_path}")