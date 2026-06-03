import os
import pandas as pd

# File path
# Resolve paths relative to this script so the script works when run from any CWD
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "data", "report.txt")

# Ensure output directory exists
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# Store extracted rows
data = []

# Open TXT file and process line-by-line to avoid loading everything into memory
# Use a tolerant decode (replace undecodable bytes) to avoid crashing on unexpected encodings
with open(file_path, "r", encoding="utf-8", errors="replace") as file:
    for line in file:
        if not line:
            continue

        # Process only @PM lines
        if line.startswith("@PM"):
            # Split using tab
            parts = line.strip().split("\t")

            # Ensure enough columns exist
            if len(parts) >= 10:
                pm_no = parts[0]
                status = parts[1]
                test_type = parts[4]

                # Convert comma decimals safely and coerce to numeric where appropriate
                value_str = parts[5].replace(",", ".")
                min_limit_str = parts[7].replace(",", ".")
                max_limit_str = parts[8].replace(",", ".")

                comment = parts[9]

                data.append([
                    pm_no,
                    status,
                    test_type,
                    value_str,
                    min_limit_str,
                    max_limit_str,
                    comment,
                ])

# Create dataframe
df = pd.DataFrame(
    data,
    columns=[
        "PM_No",
        "Status",
        "Test_Type",
        "Value",
        "Min_Limit",
        "Max_Limit",
        "Comment",
    ],
)

# Convert numeric-like columns to numeric types (coerce invalids to NaN)
for col in ("Value", "Min_Limit", "Max_Limit"):
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Display dataframe
print(df)

# Export to Excel
output_path = os.path.join(output_dir, "parsed_report.xlsx")
df.to_excel(output_path, index=False)

print(f"\nExcel file generated successfully: {output_path}")