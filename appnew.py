import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(
    page_title="Manufacturing Analytics",
    layout="wide"
)

st.title("Manufacturing Analytics Excel App")
st.markdown(
    "Upload an EOL Excel file and generate a Comment vs File Name matrix."
)


# ==========================================================
# Excel Export Helper
# ==========================================================

def to_excel_bytes(df):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(
            writer,
            sheet_name="EOL Report",
            index=False
        )

    buffer.seek(0)
    return buffer


# ==========================================================
# Matrix Generator
# ==========================================================

def generate_eol_report(
    df,
    selected_comments,
    selected_file_names
):
    required_columns = [
        "File Name",
        "Comment",
        "Value"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"Missing required column: {col}"
            )

    filtered = df[
        (df["Comment"].isin(selected_comments))
        &
        (df["File Name"].isin(selected_file_names))
    ]

    output = filtered.pivot_table(
        index="File Name",
        columns="Comment",
        values="Value",
        aggfunc="first"
    )

    output = output.reset_index()

    final_columns = ["File Name"]

    for comment in selected_comments:
        if comment in output.columns:
            final_columns.append(comment)

    output = output[final_columns]

    output["File Name"] = pd.Categorical(
        output["File Name"],
        categories=selected_file_names,
        ordered=True
    )

    output = output.sort_values(
        "File Name"
    ).reset_index(drop=True)

    return output


# ==========================================================
# Upload Excel
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if uploaded_file:

    try:

        df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()

        st.subheader("Detected Columns")

        st.write(df.columns.tolist())

        required = {
            "File Name",
            "Comment",
            "Value"
        }

        if not required.issubset(df.columns):

            st.error(
                f"""
Missing required columns.

Required:
{required}

Detected:
{set(df.columns)}
"""
            )

            st.stop()

        # ==================================================
        # Preview
        # ==================================================

        st.subheader("Input Preview")

        st.dataframe(df.head(20))

        # ==================================================
        # Unique Comments
        # ==================================================

        comments = sorted(
            df["Comment"]
            .dropna()
            .astype(str)
            .unique()
        )

        file_names = sorted(
            df["File Name"]
            .dropna()
            .astype(str)
            .unique()
        )

        # ==================================================
        # Comment Search
        # ==================================================

        st.subheader("Comment Selection")

        search_text = st.text_input(
            "Search Comment"
        )

        if search_text:

            filtered_comments = [
                c
                for c in comments
                if search_text.lower()
                in c.lower()
            ]

        else:
            filtered_comments = comments

        selected_comments = st.multiselect(
            "Select Comments (Columns)",
            options=filtered_comments
        )

        # ==================================================
        # File Name Selection
        # ==================================================

        st.subheader("File Name Selection")

        selected_file_names = st.multiselect(
            "Select File Names (Rows)",
            options=file_names,
            default=file_names
        )

        # ==================================================
        # Generate
        # ==================================================

        if st.button("Generate Report"):

            if not selected_comments:

                st.warning(
                    "Please select at least one comment."
                )

            elif not selected_file_names:

                st.warning(
                    "Please select at least one file name."
                )

            else:

                output_df = generate_eol_report(
                    df,
                    selected_comments,
                    selected_file_names
                )

                st.success(
                    "Report Generated Successfully"
                )

                st.subheader("Output Matrix")

                st.dataframe(
                    output_df,
                    use_container_width=True
                )

                excel_buffer = to_excel_bytes(
                    output_df
                )

                st.download_button(
                    label="Download Excel Report",
                    data=excel_buffer,
                    file_name="EOL_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:

        st.error(str(e))

else:

    st.info(
        "Upload an Excel file to begin."
    )