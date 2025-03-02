import csv
import re

def markdown_to_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    table_lines = lines[2:]  # Skip header separator lines
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        
        for line in table_lines:
            columns = re.split(r'\s*\|\s*', line.strip("|"))  # Split columns
            writer.writerow(columns)

input_file = "input.md"
output_file = "output.csv"
markdown_to_csv(input_file, output_file)
print(f"CSV file '{output_file}' created successfully!")

