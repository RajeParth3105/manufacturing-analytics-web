import pandas as pd
import streamlit as st
from io import BytesIO

from analytics import ManufacturingAnalytics

st.set_page_config(
    page_title="Manufacturing Analytics",
    layout="wide"
)

st.title("Manufacturing Analytics Excel App")
st.markdown(
    "Upload an Excel file and get a downloadable report in the browser."
)

mode = st.radio(
    "Choose report type",
    [
        "EOL pivot / comment matrix",
        "Analytics summary and dashboard"
    ]
)

uploaded_file = st.file_uploader(
    "Upload an Excel file (.xlsx)",
    type=["xlsx"]
)


def to_excel_bytes(dfs, sheet_names, output_name="report.xlsx"):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for df, sheet_name in zip(dfs, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    buffer.seek(0)
    return buffer


def generate_eol_report(df):
    required = {"File Name", "Comment", "Value"}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        raise ValueError(
            f"Input file must contain columns: File Name, Comment, Value. Missing: {', '.join(missing)}"
        )

    df.columns = df.columns.str.strip()
    
    # Get unique comments and file names
    comments = sorted(df["Comment"].dropna().unique())
    file_names = sorted(df["File Name"].dropna().unique())
    
    st.subheader("Select Comments (Columns)")
    st.write(f"Available comments: {len(comments)}")
    selected_comments = st.multiselect(
        "Select comments to include",
        comments,
        default=comments[:min(5, len(comments))],
        key="comment_select"
    )

    st.subheader("Select File Names (Rows)")
    st.write(f"Available file names: {len(file_names)}")
    selected_file_names = st.multiselect(
        "Select file names to include",
        file_names,
        default=file_names,
        key="filename_select"
    )

    if not selected_comments:
        st.warning("Select at least one comment to generate the report.")
        return None, None, None

    if not selected_file_names:
        st.warning("Select at least one file name to generate the report.")
        return None, None, None

    # Filter data by selected comments and file names
    filtered = df[
        (df["Comment"].isin(selected_comments)) &
        (df["File Name"].isin(selected_file_names))
    ]
    
    # Create pivot table
    output = filtered.pivot_table(
        index="File Name",
        columns="Comment",
        values="Value",
        aggfunc="first"
    ).reset_index()
    
    # Reorder columns to match user selection
    output = output[["File Name"] + selected_comments]
    
    # Reorder rows to match user selection
    output["File Name"] = pd.Categorical(
        output["File Name"],
        categories=selected_file_names,
        ordered=True
    )
    output = output.sort_values("File Name").reset_index(drop=True)
    
    return output, selected_comments, selected_file_names


def generate_analytics_report(df, file_name):
    analytics = ManufacturingAnalytics()
    analytics.process_eol_data(df, file_name)

    summary_df = analytics.get_summary_dataframe()
    segment_df = analytics.get_segment_dataframe()
    root_cause_df = analytics.get_root_cause_dataframe()

    if summary_df.empty and segment_df.empty and root_cause_df.empty:
        raise ValueError(
            "Uploaded file does not contain supported analytics columns (NOK_Count, Failure, Count)."
        )

    return summary_df, segment_df, root_cause_df


if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Cannot read Excel file: {exc}")
    else:
        st.subheader("Input preview")
        st.dataframe(df.head())

        if st.button("Generate report"):
            try:
                if mode == "EOL pivot / comment matrix":
                    output_df, selected_comments, selected_file_names = generate_eol_report(df)
                    if output_df is None:
                        st.stop()

                    st.success("EOL report generated.")
                    st.dataframe(output_df)
                    excel_buffer = to_excel_bytes(
                        [output_df],
                        ["EOL Report"],
                        output_name="EOL_Report.xlsx"
                    )
                    st.download_button(
                        label="Download EOL Report",
                        data=excel_buffer,
                        file_name="EOL_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    summary_df, segment_df, root_cause_df = generate_analytics_report(
                        df,
                        uploaded_file.name
                    )

                    st.success("Analytics dashboard generated.")
                    st.write("Summary")
                    st.dataframe(summary_df)
                    st.write("Segment analysis")
                    st.dataframe(segment_df)
                    st.write("Root cause analysis")
                    st.dataframe(root_cause_df)

                    excel_buffer = to_excel_bytes(
                        [summary_df, segment_df, root_cause_df],
                        ["Summary", "Segment Analysis", "Root Cause Analysis"],
                        output_name="Analytics_Dashboard.xlsx"
                    )
                    st.download_button(
                        label="Download Analytics Dashboard",
                        data=excel_buffer,
                        file_name="Analytics_Dashboard.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as exc:
                st.error(str(exc))
else:
    st.info("Upload an Excel file to begin.")
