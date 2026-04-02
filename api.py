from flask import Flask, jsonify
from google.cloud import bigquery

app = Flask(__name__)

# BigQuery client
client = bigquery.Client()

@app.route("/")
def home():
    return "Healthcare Analytics API Running"

# Endpoint 1 — Hospitals KPI
@app.route("/hospitals")
def hospitals():
    query = """
    SELECT *
    FROM `revature-project-488404.healthcare_analytics.fact_hospital_kpi`
    LIMIT 50
    """
    df = client.query(query).to_dataframe()
    return jsonify(df.to_dict(orient="records"))

# Endpoint 2 — Providers dimension
@app.route("/providers")
def providers():
    query = """
    SELECT *
    FROM `revature-project-488404.healthcare_analytics.dim_patient_provider`
    LIMIT 50
    """
    df = client.query(query).to_dataframe()
    return jsonify(df.to_dict(orient="records"))

# Endpoint 3 — High readmission hospitals
@app.route("/high_readmission")
def high_readmission():
    query = """
    SELECT *
    FROM `revature-project-488404.healthcare_analytics.fact_hospital_kpi`
    WHERE readmission_rate > 0.2
    LIMIT 20
    """
    df = client.query(query).to_dataframe()
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)