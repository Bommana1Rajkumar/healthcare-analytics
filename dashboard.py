import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Healthcare Intelligence Dashboard",
    layout="wide"
)

st.title("🏥 Indian Healthcare Provider Intelligence Dashboard")

# -------------------------------------------------
# LOAD DATA FROM BIGQUERY
# -------------------------------------------------
@st.cache_data
def load_data():
    client = bigquery.Client()
    query = """
    SELECT *
    FROM `revature-project-488404.healthcare_analytics.final_hospital_model`
    """
    return client.query(query).to_dataframe()

data = load_data()

# -------------------------------------------------
# STANDARDIZE COLUMN NAMES
# -------------------------------------------------
data.columns = data.columns.str.strip().str.lower()

# -------------------------------------------------
# AUTO COLUMN MAPPING ENGINE
# -------------------------------------------------
column_mapping = {}

for col in data.columns:
    if "hospital" in col and "name" in col:
        column_mapping[col] = "hospital_name"
    elif "state" in col:
        column_mapping[col] = "state"
    elif "special" in col:
        column_mapping[col] = "primary_specialty"
    elif "doctor" in col:
        column_mapping[col] = "total_doctors"
    elif "success" in col:
        column_mapping[col] = "success_ratio"
    elif "patient" in col:
        column_mapping[col] = "annual_patients"
    elif "revenue" in col:
        column_mapping[col] = "annual_revenue_inr"

data = data.rename(columns=column_mapping)

# -------------------------------------------------
# REQUIRED COLUMNS CHECK
# -------------------------------------------------
required_columns = [
    "hospital_name",
    "state",
    "primary_specialty",
    "total_doctors",
    "success_ratio",
    "annual_patients",
    "annual_revenue_inr"
]

missing_cols = [col for col in required_columns if col not in data.columns]

if missing_cols:
    st.error(f"Missing columns in BigQuery table: {missing_cols}")
    st.stop()

# -------------------------------------------------
# CLEAN NUMERIC COLUMNS
# -------------------------------------------------
numeric_cols = [
    "total_doctors",
    "success_ratio",
    "annual_patients",
    "annual_revenue_inr"
]

for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")

data[numeric_cols] = data[numeric_cols].fillna(0)
data = data.dropna(subset=["hospital_name", "state"])

filtered_data = data.copy()

# -------------------------------------------------
# HOSPITAL RANKING ENGINE
# -------------------------------------------------
def normalize(series):
    if series.max() == series.min():
        return 0
    return (series - series.min()) / (series.max() - series.min())

filtered_data["norm_revenue"] = normalize(filtered_data["annual_revenue_inr"])
filtered_data["norm_patients"] = normalize(filtered_data["annual_patients"])
filtered_data["norm_doctors"] = normalize(filtered_data["total_doctors"])

filtered_data["hospital_score"] = (
    (0.4 * filtered_data["success_ratio"]) +
    (0.3 * filtered_data["norm_revenue"]) +
    (0.2 * filtered_data["norm_patients"]) +
    (0.1 * filtered_data["norm_doctors"])
)

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Hospital Performance",
        "Revenue Intelligence",
        "Doctor & Specialty Insights"
    ]
)

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("Filters")

state_filter = st.sidebar.multiselect(
    "Select State",
    options=sorted(filtered_data["state"].unique())
)

specialty_filter = st.sidebar.multiselect(
    "Select Specialty",
    options=sorted(filtered_data["primary_specialty"].unique())
)

if state_filter:
    filtered_data = filtered_data[filtered_data["state"].isin(state_filter)]

if specialty_filter:
    filtered_data = filtered_data[
        filtered_data["primary_specialty"].isin(specialty_filter)
    ]

# -------------------------------------------------
# EXECUTIVE OVERVIEW
# -------------------------------------------------
if page == "Executive Overview":

    st.subheader("Executive Summary")

    total_revenue = filtered_data["annual_revenue_inr"].sum()
    total_doctors = filtered_data["total_doctors"].sum()
    total_patients = filtered_data["annual_patients"].sum()
    avg_success = filtered_data["success_ratio"].mean()

    revenue_million = total_revenue / 1_000_000

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Hospitals", filtered_data["hospital_name"].nunique())
    col2.metric("Total Revenue (₹ Million)", f"{round(revenue_million):,}")
    col3.metric("Total Doctors", int(total_doctors))
    col4.metric("Success Rate (%)", round(avg_success * 100))

    st.divider()

    # Operational KPIs
    st.subheader("Operational Efficiency Metrics")

    revenue_per_doctor = total_revenue / total_doctors if total_doctors > 0 else 0
    patients_per_doctor = total_patients / total_doctors if total_doctors > 0 else 0

    k1, k2 = st.columns(2)
    k1.metric("Revenue per Doctor (₹ Million)", round(revenue_per_doctor / 1_000_000))
    k2.metric("Patients per Doctor", round(patients_per_doctor))

    st.divider()

    # Create State Revenue Data
    state_rev = (
        filtered_data.groupby("state")["annual_revenue_inr"]
        .sum()
        .reset_index()
    )

    state_rev["revenue_million"] = state_rev["annual_revenue_inr"] / 1_000_000

    # BAR CHART
    st.subheader("State-wise Revenue Comparison")

    fig_bar = px.bar(
        state_rev,
        x="state",
        y="revenue_million",
        color="state",
        template="plotly_dark"
    )

    fig_bar.update_layout(
        yaxis_title="Revenue (₹ Million)",
        xaxis_title="State"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # PIE CHART
    st.subheader("Revenue Contribution by State")

    fig_pie = px.pie(
        state_rev,
        names="state",
        values="annual_revenue_inr",
        hole=0.45,
        template="plotly_dark"
    )

    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # LINE CHART
    st.subheader("Revenue Trend by State")

    fig_line = px.line(
        state_rev.sort_values("annual_revenue_inr", ascending=False),
        x="state",
        y="annual_revenue_inr",
        markers=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig_line, use_container_width=True)

# -------------------------------------------------
# HOSPITAL PERFORMANCE
# -------------------------------------------------
elif page == "Hospital Performance":

    st.subheader("🏆 Top Ranked Hospitals")

    top_ranked = filtered_data.sort_values(
        by="hospital_score",
        ascending=False
    ).head(10)

    fig_rank = px.bar(
        top_ranked,
        x="hospital_name",
        y="hospital_score",
        color="state",
        template="plotly_dark"
    )

    st.plotly_chart(fig_rank, use_container_width=True)

# -------------------------------------------------
# REVENUE INTELLIGENCE
# -------------------------------------------------
elif page == "Revenue Intelligence":

    spec_rev = (
        filtered_data.groupby("primary_specialty")["annual_revenue_inr"]
        .sum()
        .reset_index()
    )

    fig_spec_rev = px.bar(
        spec_rev,
        x="primary_specialty",
        y="annual_revenue_inr",
        color="primary_specialty",
        template="plotly_dark"
    )

    st.plotly_chart(fig_spec_rev, use_container_width=True)

# -------------------------------------------------
# DOCTOR & SPECIALTY INSIGHTS
# -------------------------------------------------
elif page == "Doctor & Specialty Insights":

    doc_spec = (
        filtered_data.groupby("primary_specialty")["total_doctors"]
        .sum()
        .reset_index()
    )

    fig_doc = px.bar(
        doc_spec,
        x="primary_specialty",
        y="total_doctors",
        color="primary_specialty",
        template="plotly_dark"
    )

    st.plotly_chart(fig_doc, use_container_width=True)

# -------------------------------------------------
# DOWNLOAD
# -------------------------------------------------
st.sidebar.download_button(
    "Download Dataset",
    filtered_data.to_csv(index=False),
    file_name="healthcare_dataset.csv"
)