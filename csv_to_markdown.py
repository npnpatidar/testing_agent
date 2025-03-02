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

def csv_to_markdown(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        rows = list(reader)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('| ' + ' | '.join(rows[0]) + ' |\n')
        file.write('|-' + '-|-'.join(['-' * len(col) for col in rows[0]]) + '-|\n')
        for row in rows[1:]:
            file.write('| ' + ' | '.join(row) + ' |\n')

# input_file = "input.md"
# output_file = "output.csv"
# markdown_to_csv(input_file, output_file)
# print(f"CSV file '{output_file}' created successfully!")

csv_input = "input.csv"
markdown_output = "output.md"
csv_to_markdown(csv_input, markdown_output)
print(f"Markdown file '{markdown_output}' created successfully!")

