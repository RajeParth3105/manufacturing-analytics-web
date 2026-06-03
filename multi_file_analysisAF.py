import os
import pandas as pd

# PATH SETUP

script_dir = os.path.dirname(os.path.abspath(__file__))

data_folder = os.path.join(script_dir, "data", "dataA", "dataAF")

output_folder = os.path.join(script_dir, "output", "outputA", "outputAF")

os.makedirs(output_folder, exist_ok=True)


# MASTER DATA STORAGE

all_data = []

# PROCESS ALL TXT FILES

for filename in os.listdir(data_folder):

    # Only process TXT files
    if filename.endswith(".txt"):

        file_path = os.path.join(data_folder, filename)

        print(f"\nProcessing: {filename}")

        # ----------------------------------------
        # DEFAULT METADATA
        # ----------------------------------------

        variant = "Unknown"
        eol = "Unknown"
        part_status = "Unknown"
        timestamp = "Unknown"

        # ----------------------------------------
        # READ FILE
        # ----------------------------------------

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            for line in file:

                line = line.strip()

                # --------------------------------
                # EXTRACT METADATA
                # --------------------------------

                if line.startswith("@GPD001"):
                    parts = line.split("\t")
                    if len(parts) > 1:
                        variant = parts[1]

                elif line.startswith("@GPD011"):
                    parts = line.split("\t")
                    if len(parts) > 1:
                        part_status = parts[1]

                elif line.startswith("@GPD009"):
                    parts = line.split("\t")
                    if len(parts) > 1:
                        timestamp = parts[1]

                elif line.startswith("@SD008"):
                    parts = line.split("\t")
                    if len(parts) > 1:
                        eol = parts[1]

                # --------------------------------
                # PROCESS PM ROWS
                # --------------------------------

                elif line.startswith("@PM"):

                    pm_parts = line.split("\t")

                    if len(pm_parts) >= 10:

                        pm_no = pm_parts[0]

                        pm_status = pm_parts[1]

                        test_type = pm_parts[4]

                        value = (
                            pm_parts[5]
                            .replace(",", ".")
                        )

                        min_limit = (
                            pm_parts[7]
                            .replace(",", ".")
                        )

                        max_limit = (
                            pm_parts[8]
                            .replace(",", ".")
                        )

                        comment = pm_parts[9]

                        # ------------------------
                        # STORE ONLY NIO FAILURES
                        # ------------------------

                        if pm_status == "NIO":

                            all_data.append({

                                "File_Name": filename,

                                "Timestamp": timestamp,

                                "EOL": eol,

                                "Variant": variant,

                                "Part_Status": part_status,

                                "PM_No": pm_no,

                                "PM_Status": pm_status,

                                "Test_Type": test_type,

                                "Value": value,

                                "Min_Limit": min_limit,

                                "Max_Limit": max_limit,

                                "Comment": comment

                            })

# ------------------------------------------------
# CREATE MASTER DATAFRAME
# ------------------------------------------------

df = pd.DataFrame(all_data)

# ------------------------------------------------
# HANDLE EMPTY DATA
# ------------------------------------------------

if df.empty:

    print("\nNo NIO failures found!")

else:

    # --------------------------------------------
    # FAILURE SUMMARY
    # --------------------------------------------

    summary = (
        df.groupby(
            ["EOL", "Variant", "Comment"]
        )
        .size()
        .reset_index(name="NOK_Count")
    )

    # --------------------------------------------
    # CALCULATE PERCENTAGE
    # --------------------------------------------

    total_failures = summary["NOK_Count"].sum()

    summary["Failure_Percentage"] = (
        summary["NOK_Count"] /
        total_failures
    ) * 100

    summary["Failure_Percentage"] = (
        summary["Failure_Percentage"]
        .round(2)
    )

    # --------------------------------------------
    # PRIORITY LOGIC
    # --------------------------------------------

    def assign_priority(percent):

        if percent >= 30:
            return "HIGH"

        elif percent >= 10:
            return "MEDIUM"

        else:
            return "LOW"

    summary["Priority"] = (
        summary["Failure_Percentage"]
        .apply(assign_priority)
    )

    # --------------------------------------------
    # SORT RESULTS
    # --------------------------------------------

    summary = summary.sort_values(
        by="Failure_Percentage",
        ascending=False
    )

    # --------------------------------------------
    # EXPORT MASTER DATA
    # --------------------------------------------

    master_output = os.path.join(
        output_folder,
        "master_nio_data_AF.xlsx"
    )

    df.to_excel(
        master_output,
        index=False
    )

    # --------------------------------------------
    # EXPORT SUMMARY
    # --------------------------------------------

    summary_output = os.path.join(
        output_folder,
        "failure_summary_AF.xlsx"
    )

    summary.to_excel(
        summary_output,
        index=False
    )

    # --------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------

    # --------------------------------------------
    # GLOBAL FAILURE COMMENT ANALYSIS
    # --------------------------------------------

    global_summary = (
        df.groupby("Comment")
        .size()
        .reset_index(name="Total_Failures")
    )

    # --------------------------------------------
    # CALCULATE GLOBAL FAILURE %
    # --------------------------------------------

    total_global_failures = (
        global_summary["Total_Failures"]
        .sum()
    )

    global_summary["Failure_Percentage"] = (
        global_summary["Total_Failures"]
        / total_global_failures
    ) * 100

    global_summary["Failure_Percentage"] = (
        global_summary["Failure_Percentage"]
        .round(2)
    )

    # --------------------------------------------
    # PRIORITY LOGIC
    # --------------------------------------------

    global_summary["Priority"] = (
        global_summary["Failure_Percentage"]
        .apply(assign_priority)
    )

    # --------------------------------------------
    # SORT BY HIGHEST FAILURE %
    # --------------------------------------------

    global_summary = global_summary.sort_values(
        by="Failure_Percentage",
        ascending=False
    )

    # --------------------------------------------
    # EXPORT GLOBAL SUMMARY
    # --------------------------------------------

    global_output = os.path.join(
        output_folder,
        "global_failure_summary_AF.xlsx"
    )

    global_summary.to_excel(
        global_output,
        index=False
    )

    print(
        f"\nGlobal failure summary saved at:\n{global_output}"
    )

    print("\n===== ANALYSIS COMPLETE =====")

    print(f"\nTotal NIO Records: {len(df)}")

    print(
        f"\nMaster data saved at:\n{master_output}"
    )

    print(
        f"\nFailure summary saved at:\n{summary_output}"
    )

