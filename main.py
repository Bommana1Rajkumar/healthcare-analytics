import pandas as pd

patients = pd.read_csv("synthea_data/patients.csv")
readmission = pd.read_csv("synthea_data/final.csv")

patients.columns = patients.columns.str.lower()
readmission.columns = readmission.columns.str.lower()

print("Missing values in Patients:")
print(patients.isnull().sum())

print("\nMissing values in Readmission:")
print(readmission.isnull().sum())

patients = patients.drop_duplicates()
readmission = readmission.drop_duplicates()

print("\nPATIENTS COLUMNS:")
print(patients.columns)

print("\nREADMISSION COLUMNS:")
print(readmission.columns)

if "state" not in patients.columns:
    print("Error: state column not found in patients dataset")

if "state" not in readmission.columns:
    print("Error: state column not found in readmission dataset")

merged_data = pd.merge(
    patients,
    readmission,
    on="state",
    how="inner"
)

print("\nMerged Dataset Shape:", merged_data.shape)
print("\nSample Data:")
print(merged_data.head())

merged_data.to_csv("merged_healthcare_dataset.csv", index=False)

print("\nMerged dataset saved successfully.")