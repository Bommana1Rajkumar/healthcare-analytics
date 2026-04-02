CREATE OR REPLACE TABLE `revature-project-488404.healthcare_analytics.final_hospital_model` AS

SELECT
    *,
    CAST(50 + RAND()*200 AS INT64) AS total_doctors,
    CAST(100 + RAND()*400 AS INT64) AS total_beds,
    CAST(number_of_discharges * (0.85 + RAND()*0.1) AS INT64) AS successful_treatments,
    CAST(number_of_discharges * (0.05 + RAND()*0.05) AS INT64) AS failed_treatments,
    ROUND(number_of_discharges * (5000 + RAND()*10000),2) AS revenue,
    ROUND(5000 + RAND()*20000,2) AS avg_treatment_cost,
    ROUND(3 + RAND()*2,2) AS patient_satisfaction
FROM `revature-project-488404.healthcare_analytics.final_hospital_model`;