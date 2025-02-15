import csv

def merge_csv_files(input_files, output_file):
    combined_data = []
    
    # Read data from each processed file
    for input_file in input_files:
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header in each file
            combined_data.extend(reader)  # Append data
    
    # Write merged data to final CSV
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Locality", "BHK", "Average Price (INR)", "Furnishing"])  # Write header
        writer.writerows(combined_data)  # Write data

# Example usage
processed_files = ["processed_rental_blr.csv", "processed_rental_hyd.csv", "processed_rental_gurg.csv"]
merge_csv_files(processed_files, "final_rental_data.csv")

print("Merged CSV saved as 'final_rental_data.csv'")
