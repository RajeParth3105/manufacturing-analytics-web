import pandas as pd
import os

# Read Excel
df = pd.read_excel(
    r"C:\Users\abhij\AIML\ManufacturingAnalytics\eol_data.xlsx"
)

# Remove leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Get all unique comments
comments = sorted(df["Comment"].dropna().unique())

print("\nAvailable Comments:\n")

for i, comment in enumerate(comments, start=1):
    print(f"{i}. {comment}")

# User selects comments
selected_indices = input(
    "\nEnter Comment numbers separated by commas: "
)

selected_comments = [
    comments[int(i.strip()) - 1]
    for i in selected_indices.split(",")
]

print("\nSelected Comments:")
for comment in selected_comments:
    print(comment)

# Filter only selected comments
filtered = df[
    df["Comment"].isin(selected_comments)
]

# Create output table
output = filtered.pivot_table(
    index="File Name",
    columns="Comment",
    values="Value",
    aggfunc="first"
)

# Convert File Name from index to first column
output = output.reset_index()

# Reorder columns exactly as user selected
output = output[
    ["File Name"] + selected_comments
]

# Export
output.to_excel(
    "Generated_Report.xlsx",
    index=False
)

print("\nReport generated successfully!")
print("Saved as Generated_Report.xlsx")