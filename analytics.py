import pandas as pd


class ManufacturingAnalytics:

    def __init__(self):

        self.summary_data = []

        self.segment_data = []

        self.root_cause_data = []

    def process_eol_data(self, df, eol_name):

        print(f"Processing EOL: {eol_name}")

        print(df.head())

        # CASE 1
        # failure_summary files

        if 'NOK_Count' in df.columns:

            total_failures = df['NOK_Count'].sum()

            avg_failure_percentage = round(
                df['Failure_Percentage'].mean(),
                2
            )

            self.summary_data.append({

                'EOL': eol_name,

                'Total NOK': total_failures,

                'Average Failure %': avg_failure_percentage
            })

            # Segment analysis

            for _, row in df.iterrows():

                self.segment_data.append({

                    'EOL': eol_name,

                    'Comment': row['Comment'],

                    'NOK_Count': row['NOK_Count'],

                    'Priority': row['Priority']
                })

        # CASE 2
        # global failure summary

        if 'Failure' in df.columns:

            for _, row in df.iterrows():

                self.root_cause_data.append({

                    'EOL': eol_name,

                    'Failure': row['Failure'],

                    'Count': row['Count']
                })

    def get_summary_dataframe(self):

        return pd.DataFrame(self.summary_data)

    def get_segment_dataframe(self):

        return pd.DataFrame(self.segment_data)

    def get_root_cause_dataframe(self):

        return pd.DataFrame(self.root_cause_data)