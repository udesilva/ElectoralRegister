# Description: This script expands the electoral register columns in an unencrypted xlsx spreadsheet.
import openpyxl
import argparse
import os
import datetime

# Create an argument parser
parser = argparse.ArgumentParser(description='Process an encrypted xlsx spreadsheet.')
parser.add_argument('xlsx_path', type=str,
                    help='Path to the encrypted xlsx spreadsheet')

# Parse the command line arguments
args = parser.parse_args()

# Load the decrypted xlsx spreadsheet
with open(args.xlsx_path, 'rb') as f:
    workbook =  openpyxl.load_workbook(args.xlsx_path)

# Create a new workbook to store the results
new_workbook = openpyxl.Workbook()
new_sheet = new_workbook.active

# record the start time
start_time = datetime.datetime.now()

# Iterate over the rows in the first sheet of the encrypted xlsx spreadsheet
sheet = workbook.active
header = None
for row in sheet.iter_rows():
    if header is None:
        header = row
        # create index by using the values of the cells in the header row to give the column number by name
        index = {cell.value: i for i, cell in enumerate(header)}
        _markers = index['Elector Markers']
        _postcode = index['PostCode']
        _lastrow = len(header) - 1
        new_sheet.append([cell.value for cell in row])  # Copy the header row to the new sheet
        continue
    
    row_ = [str(i.value).replace('\xa0', ' ')
            if i.value is not None else '' for i in row]
    changed = False

    # Exclude "B" and "G" Elector markers for EU citizens who cannot vote in UK General Elections
    if row_[_markers] in ["B", "G"]:
        continue

    # Get the postcode fields
    postcode = row_[_postcode]
    if postcode == '':
        continue
    
    if postcode in row_[_postcode+1:]:

        while row_[_lastrow] != postcode:
            row_.insert(_postcode+1,'')

        row_ = row_[:_lastrow+1]
        changed = True

    # Copy the row to the new sheet
    new_sheet.append(row_)
# Save the results to a new xlsx file
# Get the original filename
original_filename = os.path.basename(args.xlsx_path)

# Add _xp to the basename
new_filename = os.path.splitext(original_filename)[0] + '_xp.xlsx'

# Save the results to the new xlsx file
new_workbook.save(new_filename)

# record the end time
end_time = datetime.datetime.now()

# Print the time taken
print(f"Time taken: {end_time - start_time} seconds")