import pandas as pd

# Load synthea datasets
patients = pd.read_csv("patients.csv")
providers = pd.read_csv("providers.csv")
encounters = pd.read_csv("encounters.csv")
conditions = pd.read_csv("conditions.csv")
medications = pd.read_csv("medications.csv")

# Load CMS dataset
cms = pd.read_csv("final.csv")

# Preview
print("Patients Data")
print(patients.head())

print("\nCMS Data")
print(cms.head())