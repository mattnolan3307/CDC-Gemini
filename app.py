"""
Main application script orchestrating page configuration, tabs, and layout.
Run locally with: streamlit run app.py
"""
from pathlib import Path
import streamlit as st
import pandas as pd

from src.data_loader import load_and_validate_data
from src.ui_components import render_header, render_sidebar, render_kpis
import src.charts as charts

# Page Setup
st.set_page_config(
    page_title="CDC Natality Dashboard 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    base_dir = Path(__file__).resolve().parent
    csv_filename = "Provisional_Natality_2025_CDC1.csv"
    data_path = base_dir / "data" / csv_filename if (base_dir / "data" / csv_filename).exists() else base_dir / csv_filename

    try:
        raw_df = load_and_validate_data(data_path)
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    render_header()
    filtered_df = render_sidebar(raw_df)

    if filtered_df.empty:
        st.warning(
            "⚠️ No observations match your current filter selection. "
            "Please select at least one State, Month, and Sex category using the sidebar.",
            icon="⚠️"
        )
        st.stop()

    render_kpis(filtered_df)

    tab_overview, tab_geo, tab_monthly_sex, tab_table, tab_about = st.tabs([
        "📈 Overview",
        "🗺️ Geographic Analysis",
        "👥 Monthly & Sex Analysis",
        "📋 Data Table & Download",
        "📖 About the Data"
    ])

    with tab_overview:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(charts.create_monthly_trend(filtered_df), use_container_width=True)
        with c2:
            st.plotly_chart(charts.create_state_ranking(filtered_df), use_container_width=True)

    with tab_geo:
        st.plotly_chart(charts.create_choropleth_map(filtered_df), use_container_width=True)
        st.plotly_chart(charts.create_top_bottom_comparison(filtered_df, n=5), use_container_width=True)

    with tab_monthly_sex:
        st.plotly_chart(charts.create_sex_comparison(filtered_df), use_container_width=True)
        st.plotly_chart(charts.create_state_month_heatmap(filtered_df), use_container_width=True)

    with tab_table:
        st.subheader("Filtered Observation Table")
        st.caption("Inspect and download the currently selected subset.")

        display_df = filtered_df[
            ["state_of_residence", "month", "month_code", "year_code", "sex_of_infant", "births"]
        ].sort_values(by=["state_of_residence", "month_code", "sex_of_infant"])

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "state_of_residence": "State of Residence",
                "month": "Month",
                "month_code": "Month Code",
                "year_code": "Year",
                "sex_of_infant": "Infant Sex",
                "births": st.column_config.NumberColumn("Birth Count", format="%d")
            },
            hide_index=True
        )

        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_bytes,
            file_name="cdc_provisional_natality_filtered_2025.csv",
            mime="text/csv",
            use_container_width=False
        )

    with tab_about:
        st.subheader("Methodology & Pedagogical Notes")
        st.markdown(
            """
            ### Background & Analytical Context
            This dashboard was developed to guide undergraduate business analytics students through 
            exploratory data analysis (EDA), categorical time-series decomposition, and geographic aggregation.

            #### 1. Counts vs. Rates
            * **Important Distinction:** The values in this dataset are **raw birth counts**, not **birth rates** (e.g., General Fertility Rate or Crude Birth Rate).
            * Highly populated states like California and Texas naturally display the highest birth counts. To make valid cross-state comparisons of fertility propensity, analysts must normalize birth counts by the corresponding state female reproductive-age population (ages 15–44).

            #### 2. Provisional Data Caveats
            * The figures provided by the CDC National Center for Health Statistics (NCHS) are **provisional**.
            * Counts represent preliminary records reported by vital statistics jurisdictions and remain subject to retrospective revisions, delayed registration filings, and end-of-year audits.

            #### 3. Data Dictionary
            | Field | Type | Description |
            | :--- | :--- | :--- |
            | `state_of_residence` | String | US State or Federal District of mother's residence |
            | `month` | Categorical | Full calendar month name (chronologically indexed) |
            | `month_code` | Integer | Month integer identifier (1 through 12) |
            | `year_code` | Integer | Registration calendar year (2025) |
            | `sex_of_infant` | String | Infant recorded sex (`Female` or `Male`) |
            | `births` | Integer | Number of live births registered |
            """
        )

if __name__ == "__main__":
    main()
