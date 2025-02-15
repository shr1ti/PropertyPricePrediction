from sqlalchemy import create_engine
import pandas as pd
import numpy as np

# Create database connection
engine = create_engine('postgresql://settl_staging_user:SettlThe#098@settl-combined-system.cwgkzqbex6z4.ap-south-1.rds.amazonaws.com:5432/staging_settl')
connection = engine.connect()

# SQL query to fetch data
query = """
SELECT
    resident_property.property_name AS property_name,
    resident_property.id AS property_id,
    resident_property.total_opex,
    resident_property.city,
    resident_property.locality,
    ROUND(AVG(resident_contract.rent)) AS avg_rent,  
    MAX(resident_admindashboardoccupancy.occupancy_ratio) AS occupancy_ratio,  
    ROUND(AVG(EXTRACT(YEAR FROM AGE(resident_contract.end_date, resident_contract.start_date)) * 12 +
    EXTRACT(MONTH FROM AGE(resident_contract.end_date, resident_contract.start_date))), 2) AS months_of_stay
FROM
    resident_property
JOIN 
    resident_admindashboardoccupancy 
    ON resident_property.id = resident_admindashboardoccupancy.property_id
LEFT JOIN
    resident_contract 
    ON resident_property.id = resident_contract.property_id
WHERE
    resident_property.status = 'live'
    AND resident_contract.status != 'cancelled'
GROUP BY
    resident_property.id;
"""

# Load data from database into a DataFrame
df = pd.read_sql(query, connection)
connection.close()

# Load the Excel file
excel_file_path = r"C:\Users\shrit\Downloads\ML Model Data .xlsx"
excel_df = pd.read_excel(excel_file_path, sheet_name='Cost Price')  

# Merge SQL and Excel data on property_name
combined_df = pd.merge(df, excel_df, on='property_name', how='left')

# Calculate Gross Margin and append it to the DataFrame
combined_df["GrossMargin"] = np.where(
    combined_df["avg_rent"].notna() & (combined_df["avg_rent"] != 0),  # Avoid division by zero
    ((combined_df["avg_rent"] - combined_df["CP/ Room"]) / combined_df["avg_rent"]) * 100,
    np.nan  
)

print(combined_df.head())

