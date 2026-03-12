import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Healthcare Analytics Dashboard", layout="wide")

st.title("Healthcare Provider Analytics Dashboard")

# LOAD DATA
kpi_data = pd.read_csv("hospital_kpi_dataset.csv")

# CLEAN DATA
kpi_data.columns = kpi_data.columns.str.lower()
kpi_data["number of discharges"] = pd.to_numeric(kpi_data["number of discharges"], errors="coerce")
kpi_data["number of readmissions"] = pd.to_numeric(kpi_data["number of readmissions"], errors="coerce")
kpi_data["readmission_rate"] = pd.to_numeric(kpi_data["readmission_rate"], errors="coerce")

kpi_data = kpi_data.dropna()

# SIDEBAR FILTERS
st.sidebar.header("Filters")

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All"] + sorted(kpi_data["state"].dropna().unique())
)

if selected_state != "All":
    filtered_data = kpi_data[kpi_data["state"] == selected_state]
else:
    filtered_data = kpi_data

selected_hospital = st.sidebar.selectbox(
    "Select Hospital",
    ["All"] + sorted(filtered_data["facility name"].unique())
)

if selected_hospital != "All":
    filtered_data = filtered_data[filtered_data["facility name"] == selected_hospital]

# KPI CARDS
col1, col2, col3 = st.columns(3)

col1.metric("Total Hospitals", filtered_data["facility name"].nunique())
col2.metric("Total Discharges", int(filtered_data["number of discharges"].sum()))
col3.metric("Avg Readmission Rate", round(filtered_data["readmission_rate"].mean(), 3))

st.divider()

# HOSPITAL RANKING
st.subheader("Hospital Ranking")

view_option = st.radio(
    "View",
    ["Top 10 by Readmission Rate", "Bottom 10 by Readmission Rate"],
    horizontal=True
)

if view_option == "Top 10 by Readmission Rate":
    ranking_data = filtered_data.sort_values(by="readmission_rate", ascending=False).head(10)
else:
    ranking_data = filtered_data.sort_values(by="readmission_rate", ascending=True).head(10)

fig_rank = px.bar(
    ranking_data,
    x="facility name",
    y="readmission_rate",
    color="readmission_rate"
)

st.plotly_chart(fig_rank, use_container_width=True)

st.divider()

# SCATTER PLOT
st.subheader("Discharges vs Readmissions")

scatter_data = filtered_data.copy()

scatter_data = scatter_data.dropna(subset=[
    "number of discharges",
    "number of readmissions",
    "readmission_rate"
])

fig_scatter = px.scatter(
    scatter_data,
    x="number of discharges",
    y="number of readmissions",
    color="readmission_rate",
    hover_name="facility name"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# READMISSION DISTRIBUTION
st.subheader("Readmission Rate Distribution")

fig_hist = px.histogram(
    filtered_data,
    x="readmission_rate",
    nbins=20,
    color_discrete_sequence=["red"]
)

st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# STATE COMPARISON
st.subheader("State Comparison")

state_data = filtered_data.groupby("state")["readmission_rate"].mean().reset_index()

fig_state = px.bar(
    state_data,
    x="state",
    y="readmission_rate",
    color="readmission_rate"
)

st.plotly_chart(fig_state, use_container_width=True)

st.divider()

# COMPARE HOSPITALS
st.subheader("Compare Hospitals")

hosp1 = st.selectbox("Select Hospital 1", filtered_data["facility name"].unique())
hosp2 = st.selectbox("Select Hospital 2", filtered_data["facility name"].unique())

data1 = filtered_data[filtered_data["facility name"] == hosp1]
data2 = filtered_data[filtered_data["facility name"] == hosp2]

comp_df = pd.DataFrame({
    "Hospital": [hosp1, hosp2],
    "Readmission Rate": [
        data1["readmission_rate"].mean(),
        data2["readmission_rate"].mean()
    ]
})

fig_compare = px.bar(comp_df, x="Hospital", y="Readmission Rate", color="Hospital")
st.plotly_chart(fig_compare, use_container_width=True)

st.divider()

# KEY INSIGHTS
st.subheader("Key Insights")

highest = filtered_data.loc[filtered_data["readmission_rate"].idxmax()]
lowest = filtered_data.loc[filtered_data["readmission_rate"].idxmin()]

st.success(f"Highest Readmission Rate: {highest['facility name']} ({round(highest['readmission_rate'],3)})")
st.info(f"Lowest Readmission Rate: {lowest['facility name']} ({round(lowest['readmission_rate'],3)})")

corr = filtered_data["number of discharges"].corr(filtered_data["number of readmissions"])
st.warning(f"Correlation between Discharges and Readmissions: {round(corr,2)}")

st.divider()

# DOWNLOAD BUTTON
st.download_button(
    "Download Filtered Data",
    filtered_data.to_csv(index=False),
    file_name="filtered_healthcare_data.csv"
)