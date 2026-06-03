import pandas as pd
import os

# ----------------------------------------
# FILE PATHS
# ----------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(
    script_dir,
    "output",
    "parsed_report.xlsx"
)

output_file = os.path.join(
    script_dir,
    "Failure_Summary",
    "failure_summary1.xlsx"
)

# ----------------------------------------
# READ EXCEL FILE
# ----------------------------------------

df = pd.read_excel(input_file)

# ----------------------------------------
# KEEP ONLY NIO FAILURES
# ----------------------------------------

df_nio = df[df["Status"] == "NIO"]

# ----------------------------------------
# COUNT FAILURE COMMENTS
# ----------------------------------------

failure_counts = (
    df_nio["Comment"]
    .value_counts()
    .reset_index()
)

failure_counts.columns = [
    "Failure_Comment",
    "NOK_Count"
]

# ----------------------------------------
# CALCULATE FAILURE PERCENTAGE
# ----------------------------------------

total_failures = failure_counts["NOK_Count"].sum()

failure_counts["Failure_Percentage"] = (
    failure_counts["NOK_Count"] / total_failures
) * 100

# Round percentage values
failure_counts["Failure_Percentage"] = (
    failure_counts["Failure_Percentage"]
    .round(2)
)

# ----------------------------------------
# ASSIGN PRIORITY LEVELS
# ----------------------------------------

def assign_priority(percent):

    if percent >= 30:
        return "HIGH"

    elif percent >= 10:
        return "MEDIUM"

    else:
        return "LOW"

failure_counts["Priority"] = (
    failure_counts["Failure_Percentage"]
    .apply(assign_priority)
)

# ----------------------------------------
# SORT BY HIGHEST FAILURE %
# ----------------------------------------

failure_counts = failure_counts.sort_values(
    by="Failure_Percentage",
    ascending=False
)

# ----------------------------------------
# DISPLAY RESULTS
# ----------------------------------------

print("\n===== FAILURE SUMMARY =====\n")

print(failure_counts)

# ----------------------------------------
# EXPORT TO EXCEL
# ----------------------------------------

failure_counts.to_excel(
    output_file,
    index=False
)

print("\nFailure summary Excel generated successfully!")
print(f"\nSaved at:\n{output_file}")