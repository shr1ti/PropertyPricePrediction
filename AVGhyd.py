import csv
from collections import defaultdict

def process_rental_data(input_file, output_file):
    property_data = defaultdict(list)  # Corrected initialization
    
    # Read data from CSV and process
    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        
        for row in reader:
            locality, bhk, price, furnishing = row
            bhk = int(bhk)
            price_per_bhk = int(price) // bhk  # Compute price per 1 BHK
            property_data[(locality, furnishing)].append(price_per_bhk)
    
    # Compute averages
    processed_data = []
    for (locality, furnishing), prices in property_data.items():
        avg_price = sum(prices) // len(prices)  # Average price per furnishing type
        processed_data.append([locality, 1, avg_price, furnishing])
    
    # Write processed data to output CSV
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Locality", "BHK", "Average Price (INR)", "Furnishing"])
        writer.writerows(processed_data)

# Example usage
process_rental_data("rental_hyd.csv", "processed_rental_hyd.csv")
