import csv
from collections import defaultdict

def process_rental_data(input_files, output_file):
    property_data = defaultdict(lambda: defaultdict(list))
    
    # Read data from multiple CSV files and process
    for input_file in input_files:
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            
            for row in reader:
                locality, bhk, price, furnishing = row
                bhk = int(bhk)
                price = int(price) // bhk  # Compute average price of a 1BHK
                property_data[(locality, 1)][furnishing].append(price)
    
    # Compute averages for each locality and furnishing type
    processed_data = []
    for (locality, bhk), furnishing_dict in property_data.items():
        for furnishing, prices in furnishing_dict.items():
            avg_price = sum(prices) // len(prices)  # Average price per furnishing type
            processed_data.append([locality, bhk, avg_price, furnishing])
    
    # Write processed data to output CSV
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Locality", "BHK", "averageprice", "Furnishing"])
        writer.writerows(processed_data)

# Example usage
process_rental_data(["rental_blr.csv", "rental_blr2.csv"], "processed_rental_blr.csv")
