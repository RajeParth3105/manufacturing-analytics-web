import os
import pandas as pd


class ReportGenerator:

    def __init__(self, output_folder):
        self.output_folder = output_folder

    def generate_dashboard(
        self,
        summary_df,
        segment_df,
        root_cause_df
    ):

        output_path = os.path.join(
            self.output_folder,
            'consolidated_dashboard.xlsx'
        )

        with pd.ExcelWriter(
            output_path,
            engine='xlsxwriter'
        ) as writer:

            summary_df.to_excel(
                writer,
                sheet_name='EOL Summary',
                index=False
            )

            segment_df.to_excel(
                writer,
                sheet_name='Segment Analysis',
                index=False
            )

            root_cause_df.to_excel(
                writer,
                sheet_name='Root Cause Analysis',
                index=False
            )

        print(f"Dashboard generated: {output_path}")