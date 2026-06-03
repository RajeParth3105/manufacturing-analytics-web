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


def parse_index_selection(selection_str, max_index, item_name):
    if not selection_str:
        return []

    selected = set()
    parts = [part.strip() for part in selection_str.split(",") if part.strip()]
    for part in parts:
        if "-" in part:
            bounds = [x.strip() for x in part.split("-", 1)]
            if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
                raise ValueError(
                    f"Invalid {item_name} range: '{part}'. Use numbers or ranges like 1-3."
                )
            start = int(bounds[0])
            end = int(bounds[1])
            if start > end:
                raise ValueError(
                    f"Invalid {item_name} range: '{part}'. Start must be <= end."
                )
            for idx in range(start, end + 1):
                if 1 <= idx <= max_index:
                    selected.add(idx)
        else:
            if not part.isdigit():
                raise ValueError(
                    f"Invalid {item_name} index: '{part}'. Use only numbers."
                )
            idx = int(part)
            if 1 <= idx <= max_index:
                selected.add(idx)

    if not selected:
        raise ValueError(f"No valid {item_name} indexes were selected.")

    return sorted(selected)


def generate_eol_report(df, selected_comments, selected_file_names):
    required = {"File Name", "Comment", "Value"}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        raise ValueError(
            f"Input file must contain columns: File Name, Comment, Value. Missing: {', '.join(missing)}"
        )

    df.columns = df.columns.str.strip()
    filtered = df[
        (df["Comment"].isin(selected_comments)) &
        (df["File Name"].isin(selected_file_names))
    ]

    output = filtered.pivot_table(
        index="File Name",
        columns="Comment",
        values="Value",
        aggfunc="first"
    ).reset_index()

    output = output[["File Name"] + selected_comments]

    output["File Name"] = pd.Categorical(
        output["File Name"],
        categories=selected_file_names,
        ordered=True
    )
    output = output.sort_values("File Name").reset_index(drop=True)

    return output

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

        if mode == "EOL pivot / comment matrix":
            comments = sorted(df["Comment"].dropna().unique())
            file_names = sorted(df["File Name"].dropna().unique())

            st.subheader("Available comment values")
            st.write(
                "There are many unique comments. Use the index numbers below to select which comments "
                "should become columns in the output matrix."
            )
            comment_index_df = pd.DataFrame(
                {
                    "Index": range(1, len(comments) + 1),
                    "Comment": comments
                }
            )
            with st.expander("Show unique comments and their indexes", expanded=False):
                st.dataframe(comment_index_df)

            comment_selection = st.text_input(
                "Select comment indexes (e.g. 1,3,5-8):",
                value="1-5",
                key="comment_index_input"
            )

            st.subheader("Available file names")
            st.write(
                "There are many file names. Use the index numbers below to select which file names "
                "should become rows in the output matrix."
            )
            filename_index_df = pd.DataFrame(
                {
                    "Index": range(1, len(file_names) + 1),
                    "File Name": file_names
                }
            )
            with st.expander("Show file name indexes", expanded=False):
                st.dataframe(filename_index_df)

            filename_selection = st.text_input(
                "Select file name indexes (e.g. 1,2,4-6):",
                value="1-5",
                key="filename_index_input"
            )

            if st.button("Generate report"):
                try:
                    selected_comment_indexes = parse_index_selection(
                        comment_selection,
                        len(comments),
                        "comment"
                    )
                    selected_filename_indexes = parse_index_selection(
                        filename_selection,
                        len(file_names),
                        "file name"
                    )

                    selected_comments = [comments[i - 1] for i in selected_comment_indexes]
                    selected_file_names = [file_names[i - 1] for i in selected_filename_indexes]

                    output_df = generate_eol_report(
                        df,
                        selected_comments,
                        selected_file_names
                    )

                    st.success("EOL report generated.")
                    st.write("Selected comments:")
                    st.write(selected_comments)
                    st.write("Selected file names:")
                    st.write(selected_file_names)
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
                except Exception as exc:
                    st.error(str(exc))
        else:
            if st.button("Generate report"):
                try:
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
                        mime="application/vnd.openxmlformats-officedocument-spreadsheetml.sheet"
                    )
                except Exception as exc:
                    st.error(str(exc))
else:
    st.info("Upload an Excel file to begin.")
