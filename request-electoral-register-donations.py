# Script to read a CSV file of donations and request the electoral register for the donors who gave more than £50 since 31st May 2024. Also flag up anyone who does not have a UK address
# Usage: python request-electoral-register-donations.py donations.csv --apikey WDIV_API_KEY
import os
import csv
import argparse
from dotenv import load_dotenv

#from scrape_wdiv import lookup_address
from scrape_elcom import lookup_address

# import an env file in the same directory as the script
load_dotenv()

# Donations of more than £50 since 31st May 2024 need to be checked for eligibility
DONATION_START_DATE = "2024/05/31 00:00:00"
DONATION_CURRENCY = "GBP"
DONATION_MIN = 50.00 


# get the name of the CSV file using argparse as parameter donation_file
parser = argparse.ArgumentParser()
# Add a required argument for the CSV file
parser.add_argument("donation_file", help="name of the CSV file", default="donations.csv", nargs='?')
# Add an optional argument for checked_ok with a default value of checked_ok.csv
parser.add_argument("--checked_ok", help="name of the output CSV file for checked entries", default="checked_ok.csv")
args = parser.parse_args()

# read the checked_ok file into a dictionary of email,reference if it exists
checked_ok = {}
if os.path.exists(args.checked_ok):
    with open(args.checked_ok, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            checked_ok[row['email']] = row['reference']

# Read the Donations CSV file
with open(args.donation_file, newline='') as csvfile:
    # read each row of the CSV file
    reader = csv.DictReader(csvfile)
    for row in reader:
        # get the postcode from the row
        POSTCODE = row['Postal Code']
        full_address = ' '.join([ row[i] for i in ("Address","Address 2","City")])
        address = row['Address']
        country = row['Country']
        currency = row['Currency']
        amount = row['Amount']
        name = row['Name']


        # check if the donation is more than £50 and the date is after 31st May 2024       
        if row['Donated At'] < DONATION_START_DATE:
            continue
        
        # check if the donation is more than £50
        if float(row['Amount']) <= DONATION_MIN:
            continue

        print("=" * 40)

        # check if the donor has already been checked
        if ref := checked_ok.get(row['Donor Email']):
            print(f"Already checked {name} ({POSTCODE}) with reference {ref}")
            continue

        if row['Currency'] != DONATION_CURRENCY or country != "United Kingdom":
            print(f"Donation of {currency}{amount} from {name} in {country}")
            print(f"Email address: {row['Donor Email']}")
            print(f"Comment: {row['Donor Comment']}")
                  
            continue
        
        print(f"Checking {row['Name']} ({POSTCODE}) donation of {row['Currency']}"
              f"{row['Amount']} at {row['Donated At']}")
        
        constituency, email = lookup_address(POSTCODE, address)
        if email is None:
            print(f"Failed to get Electoral Services email for {row['Name']}")
            print(f"  Address: {full_address} {country}")
            print(f"  Email: {row['Donor Email']}")
            print(f"  Comment: {row['Donor Comment']}")
            continue
        
        # matches = [i for i in info['knownAddresses']
        #            if i.replace(",","").casefold() == full_address.casefold().replace("  "," ")]
        # # process info
        # if len(matches) == 0:
        #     print(f"{row['Name']} address '{full_address}' not matched!")
        #     print(f"Email: {row['Donor Email']} Comment: {row['Donor Comment']}")
        #     for i in info['knownAddresses']:
        #         print(f"  {i}")
        #     continue
        
        # print(f"{row['Name']} matched at '{full_address}'")
        # print(f"  Constituency: {info['constituency']}")


        pass
        
