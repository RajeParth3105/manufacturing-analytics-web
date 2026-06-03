import pandas as pd
import streamlit as st
from io import BytesIO
import plotly.express as px

from txt_processor import process_txt_files

st.set_page_config(
    page_title="Manufacturing Failure Analytics",
    layout="wide"
)

st.title("Manufacturing Failure Analytics")
st.write("Upload multiple TXT files exported from EOL.")

uploaded_files = st.file_uploader(
    "Upload TXT files",
    type=["txt"],
    accept_multiple_files=True
)

# ── Process files and cache in session state ──────────────────────────────────
if uploaded_files:
    if st.button("Generate Analytics"):
        try:
            master_df, summary_df, global_df = process_txt_files(uploaded_files)
            st.session_state["master_df"]  = master_df
            st.session_state["summary_df"] = summary_df
            st.session_state["global_df"]  = global_df
            st.session_state["processed"]  = True
        except Exception as e:
            st.error(f"Failed to process files: {e}")

# ── All display logic runs from session state (survives filter reruns) ─────────
if st.session_state.get("processed"):

    master_df  = st.session_state["master_df"]
    summary_df = st.session_state["summary_df"]
    global_df  = st.session_state["global_df"]

    st.success("Analysis complete!")

    # ── Filters (outside button block so they react live) ─────────────────────
    st.markdown("### Filters")
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        selected_eols = st.multiselect(
            "Filter by EOL",
            options=sorted(master_df["EOL"].unique()),
            default=sorted(master_df["EOL"].unique())
        )

    with col_f2:
        selected_variants = st.multiselect(
            "Filter by Variant",
            options=sorted(master_df["Variant"].unique()),
            default=sorted(master_df["Variant"].unique())
        )

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered_master = master_df[
        (master_df["EOL"].isin(selected_eols)) &
        (master_df["Variant"].isin(selected_variants))
    ]

    filtered_global = (
        filtered_master
        .groupby("Comment")
        .size()
        .reset_index(name="Total_Failures")
        .sort_values("Total_Failures", ascending=False)
    )

    filtered_summary = (
        filtered_master
        .groupby(["EOL", "Variant", "Comment"])
        .size()
        .reset_index(name="NOK_Count")
    )

    # ── KPI cards (filtered) ──────────────────────────────────────────────────
    st.markdown("### KPI Overview")
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Total NIO Records",  len(filtered_master))
    with k2:
        st.metric("Failure Types",      filtered_global["Comment"].nunique())
    with k3:
        st.metric("Variants",           filtered_master["Variant"].nunique())
    with k4:
        st.metric("EOLs",               filtered_master["EOL"].nunique())

    # ── Pareto chart (filtered, top 15) ───────────────────────────────────────
    st.markdown("### Top Failure Comments")
    pareto_df = filtered_global.head(15)

    if not pareto_df.empty:
        fig = px.bar(
            pareto_df,
            x="Comment",
            y="Total_Failures",
            title="Top 15 Failure Comments (Pareto)",
            labels={"Comment": "Failure Comment", "Total_Failures": "Count"},
            color="Total_Failures",
            color_continuous_scale="Reds"
        )
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

    # ── Data tables ───────────────────────────────────────────────────────────
    st.markdown("### Global Failure Summary")
    st.dataframe(filtered_global, use_container_width=True)

    st.markdown("### Failure Summary by EOL / Variant")
    st.dataframe(filtered_summary, use_container_width=True)

    # ── Excel export (filtered data) ──────────────────────────────────────────
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        filtered_master.to_excel(
            writer, sheet_name="Master Data",      index=False
        )
        filtered_summary.to_excel(
            writer, sheet_name="Failure Summary",  index=False
        )
        filtered_global.to_excel(
            writer, sheet_name="Global Summary",   index=False
        )
    buffer.seek(0)

    st.download_button(
        label="⬇ Download Analytics Workbook",
        data=buffer,
        file_name="Manufacturing_Analytics.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )