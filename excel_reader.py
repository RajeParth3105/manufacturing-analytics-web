import os
import pandas as pd


class ExcelReader:

    def __init__(self, base_path):
        self.base_path = base_path

    def find_excel_files(self):
        excel_files = []

        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".xlsx"):
                    full_path = os.path.join(root, file)
                    excel_files.append(full_path)

        return excel_files

    def read_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None