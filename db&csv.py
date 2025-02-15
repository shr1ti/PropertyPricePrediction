import pandas as pd
import numpy as np
import csv
from sqlalchemy import create_engine

# ✅ Step 1: Fetch Data from PostgreSQL Database
engine = create_engine('postgresql://settl_staging_user:SettlThe#098@settl-combined-system.cwgkzqbex6z4.ap-south-1.rds.amazonaws.com:5432/staging_settl')
connection = engine.connect()

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

df_sql = pd.read_sql(query, connection)
connection.close()

# ✅ Step 2: Load Excel Data
excel_file_path = r"C:\Users\shrit\Downloads\ML Model Data .xlsx"
df_excel = pd.read_excel(excel_file_path, sheet_name='Cost Price')  

# ✅ Step 3: Merge SQL & Excel Data (Keep "property_id" and "property_name")
df_combined = pd.merge(df_sql, df_excel, on='property_name', how='left')

# ✅ Step 4: Calculate Gross Margin
df_combined["GrossMargin"] = np.where(
    df_combined["avg_rent"].notna() & (df_combined["avg_rent"] != 0),  # Avoid division by zero
    ((df_combined["avg_rent"] - df_combined["CP/ Room"]) / df_combined["avg_rent"]) * 100,
    np.nan  
)

# ✅ Step 5: Read and Transform Processed Rental CSV Data
def merge_csv_files(input_files):
    combined_data = []
    
    for input_file in input_files:
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header in each file
            
            for row in reader:
                combined_data.append(row)
    
    df = pd.DataFrame(combined_data, columns=["Locality", "BHK", "Average Price (INR)", "Furnishing"])
    
    # Convert price to numeric
    df["Average Price (INR)"] = pd.to_numeric(df["Average Price (INR)"])
    
    # Pivot table to create separate columns for each furnishing type
    df_pivot = df.pivot(index="Locality", columns="Furnishing", values="Average Price (INR)").reset_index()
    df_pivot.columns = ["Locality", "Furnished Price", "Semi-Furnished Price", "Unfurnished Price"]
    
    return df_pivot

# Merge rental CSV data
processed_files = ["processed_rental_blr.csv", "processed_rental_hyd.csv", "processed_rental_gurg.csv"]
df_csv = merge_csv_files(processed_files)

# ✅ Step 6: Merge All Data (SQL + Excel + CSV) and Keep Property ID & Name
df_final = pd.merge(df_combined, df_csv, left_on="locality", right_on="Locality", how="left")

# Drop duplicate "Locality" column since "locality" from SQL is already present
df_final.drop(columns=["Locality"], inplace=True)

# ✅ Step 7: Save Final Data to CSV with "property_id" and "property_name"
final_output_file = "final_merged_data.csv"
df_final.to_csv(final_output_file, index=False)

print(f"Merged data saved as '{final_output_file}'")
