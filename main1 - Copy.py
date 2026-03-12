import pandas as pd
import numpy as np

patients = pd.read_csv("synthea_data/patients.csv")
providers = pd.read_csv("synthea_data/providers.csv")
encounters = pd.read_csv("synthea_data/encounters.csv")
readmission = pd.read_csv("synthea_data/final.csv")

patients.columns = patients.columns.str.lower()
providers.columns = providers.columns.str.lower()
encounters.columns = encounters.columns.str.lower()
readmission.columns = readmission.columns.str.lower()

patient_encounters = pd.merge(
    patients,
    encounters,
    left_on="id",
    right_on="patient",
    how="inner"
)

print("Patient-Encounter Shape:", patient_encounters.shape)

patient_provider = pd.merge(
    patient_encounters,
    providers,
    left_on="provider",
    right_on="id",
    how="inner"
)

print("Patient-Provider Shape:", patient_provider.shape)

final_dataset = pd.merge(
    patient_provider,
    readmission,
    left_on="state_y",
    right_on="state",
    how="inner"
)

print("Final Dataset Shape:", final_dataset.shape)

final_dataset["number of readmissions"] = pd.to_numeric(
    final_dataset["number of readmissions"], errors="coerce"
)

final_dataset["number of discharges"] = pd.to_numeric(
    final_dataset["number of discharges"], errors="coerce"
)

final_dataset["readmission_rate"] = (
    final_dataset["number of readmissions"] /
    final_dataset["number of discharges"]
)

hospital_kpi = final_dataset.groupby(
    ["facility name", "state"]
).agg({
    "number of discharges": "sum",
    "number of readmissions": "sum"
}).reset_index()

hospital_kpi["readmission_rate"] = (
    hospital_kpi["number of readmissions"] /
    hospital_kpi["number of discharges"]
)

indian_hospitals = [
    "AIIMS Delhi",
    "Apollo Hospitals Chennai",
    "Narayana Health Bangalore",
    "Yashoda Hospitals Hyderabad",
    "Fortis Mumbai",
    "CMC Vellore",
    "KIMS Hyderabad"
]

hospital_kpi["facility name"] = np.random.choice(indian_hospitals, size=len(hospital_kpi))

indian_cities = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Mumbai",
    "Delhi",
    "Kolkata",
    "Pune"
]

hospital_kpi["city"] = np.random.choice(indian_cities, size=len(hospital_kpi))

print(hospital_kpi.head())

final_dataset.to_csv("final_healthcare_dataset.csv", index=False)
hospital_kpi.to_csv("hospital_kpi_dataset.csv", index=False)

sample_data = final_dataset.sample(50000)
sample_data.to_csv("sample_healthcare_dataset.csv", index=False)

print("All datasets saved successfully.")