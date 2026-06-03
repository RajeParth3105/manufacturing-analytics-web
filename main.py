import os
import sys

from excel_reader import ExcelReader
from analytics import ManufacturingAnalytics
from report_generation import ReportGenerator
from graph_generator import GraphGenerator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PATH = os.path.join(BASE_DIR, 'output')
OUTPUT_PATH = os.path.join(BASE_DIR, 'reports')

print("INPUT PATH:", INPUT_PATH)
print("OUTPUT PATH:", OUTPUT_PATH)


def extract_eol_name(file_path):

    folders = file_path.split(os.sep)

    for folder in folders:

        if folder.startswith('output'):

            return folder.replace('output', '')

    return 'UNKNOWN'


if __name__ == '__main__':

    print("\nSTEP 1: Initializing Classes")

    reader = ExcelReader(INPUT_PATH)

    analytics = ManufacturingAnalytics()

    report_generator = ReportGenerator(OUTPUT_PATH)

    graph_generator = GraphGenerator(OUTPUT_PATH)

    print("\nSTEP 2: Searching Excel Files")

    excel_files = reader.find_excel_files()

    print(f"\nFound {len(excel_files)} Excel files")

    print(excel_files)

    print("\nSTEP 3: Processing Files")

    for file in excel_files:

        print(f"\nProcessing File: {file}")

        df = reader.read_excel(file)

        if df is None:

            print("DataFrame is None")

            continue

        print("Columns Found:")
        print(df.columns)

        eol_name = extract_eol_name(file)

        analytics.process_eol_data(df, eol_name)

    print("\nSTEP 4: Creating DataFrames")

    summary_df = analytics.get_summary_dataframe()

    segment_df = analytics.get_segment_dataframe()

    root_cause_df = analytics.get_root_cause_dataframe()

    print(summary_df)

    print("\nSTEP 5: Generating Dashboard")

    report_generator.generate_dashboard(
        summary_df,
        segment_df,
        root_cause_df
    )
    print("\nSTEP 6: Generating Graphs")

    graph_generator.production_summary_graph(summary_df)

    graph_generator.failure_rate_graph(summary_df)

    graph_generator.top_failures_graph(root_cause_df)

    print("\nDONE")