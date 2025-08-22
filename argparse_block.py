import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Fetch school lunch menu from LinqConnect API and generate ICS calendar file.')
parser.add_argument('--start-date', required=True, help='Start date in MM-DD-YYYY format')
parser.add_argument('--end-date', required=True, help='End date in MM-DD-YYYY format')
parser.add_argument('--building-id', required=True, help='Building ID for the school')
parser.add_argument('--district-id', required=True, help='District ID for the school')
args = parser.parse_args()

# Use command line arguments
start_date = args.start_date
end_date = args.end_date
building_id = args.building_id
district_id = args.district_id