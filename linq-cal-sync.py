#!python3

import requests
from ics import Calendar, Event
from datetime import datetime
import json
import pytz

import argparse
import re
import yaml
from datetime import datetime, timedelta

# Parse command line arguments
parser = argparse.ArgumentParser(description='Fetch school lunch menu from LinqConnect API and generate ICS calendar file.')
parser.add_argument('--start-date', help='Start date in MM-DD-YYYY format or relative duration (e.g., 1m, 2w, 5d)')
parser.add_argument('--end-date', help='End date in MM-DD-YYYY format or relative duration (e.g., 1m, 2w, 5d)')
parser.add_argument('--building-id', help='Building ID for the school')
parser.add_argument('--district-id', help='District ID for the school')
parser.add_argument('--config', default='config.yaml', help='Path to YAML configuration file')
args = parser.parse_args()

# Load configuration from YAML file
try:
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    print(f"Configuration file {args.config} not found.")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing YAML configuration: {e}")
    exit(1)

# Use command line arguments if provided, otherwise fall back to config file
start_date = args.start_date or config.get('default_start_date')
end_date = args.end_date or config.get('default_end_date')
building_id = args.building_id or config.get('building_id')
district_id = args.district_id or config.get('district_id')

# Validate required configuration
if not all([start_date, end_date, building_id, district_id]):
    print("Error: Missing required configuration. Please provide all values via command line or config file.")
    exit(1)


def parse_date_range(start_date_str, end_date_str):
    """
    Parse date range from command line arguments.
    Supports MM-DD-YYYY format, relative durations (1m, 2w, 5d), and special values (today, tomorrow).
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Handle special cases for start_date
    if start_date_str.lower() == 'today':
        start_date = today
    elif start_date_str.lower() == 'tomorrow':
        start_date = today
    elif re.match(r'^\d+[dwmy]$', start_date_str.lower()):
        # Duration specified, start from today
        duration = start_date_str.lower()
        number = int(duration[:-1])
        unit = duration[-1]
        
        start_date = today
        
        if unit == 'd':
            end_date = today + timedelta(days=number)
        elif unit == 'w':
            end_date = today + timedelta(weeks=number)
        elif unit == 'm':
            # Approximate month as 30 days
            end_date = today + timedelta(days=number * 30)
        elif unit == 'y':
            # Approximate year as 365 days
            end_date = today + timedelta(days=number * 365)
            
        return start_date.strftime('%m-%d-%Y'), end_date.strftime('%m-%d-%Y')
    else:
        # Parse as MM-DD-YYYY
        start_date = datetime.strptime(start_date_str, '%m-%d-%Y').date()
    
    # Handle special cases for end_date
    if end_date_str.lower() == 'today':
        end_date = today
    elif end_date_str.lower() == 'tomorrow':
        end_date = tomorrow
    elif re.match(r'^\d+[dwmy]$', end_date_str.lower()):
        # Parse duration from start_date
        duration = end_date_str.lower()
        number = int(duration[:-1])
        unit = duration[-1]
        
        if unit == 'd':
            end_date = start_date + timedelta(days=number)
        elif unit == 'w':
            end_date = start_date + timedelta(weeks=number)
        elif unit == 'm':
            # Approximate month as 30 days
            end_date = start_date + timedelta(days=number * 30)
        elif unit == 'y':
            # Approximate year as 365 days
            end_date = start_date + timedelta(days=number * 365)
            
        return start_date_str, end_date.strftime('%m-%d-%Y')
    else:
        # Parse as MM-DD-YYYY
        end_date = datetime.strptime(end_date_str, '%m-%d-%Y').date()
    
    return start_date.strftime('%m-%d-%Y'), end_date.strftime('%m-%d-%Y')

# Parse and validate date range
start_date, end_date = parse_date_range(start_date, end_date)

# Define US Eastern Timezone
eastern_tz = pytz.timezone("America/New_York")

# API endpoint with variables
api_url = f"https://api.linqconnect.com/api/FamilyMenu?buildingId={building_id}&districtId={district_id}&startDate={start_date}&endDate={end_date}"

print("Fetching data from API...")
response = requests.get(api_url)

# Check for errors in response
if response.status_code != 200:
    print(f"Error fetching data! HTTP Status Code: {response.status_code}")
    print("Response Text:", response.text)
    exit()

# Try to parse JSON response
try:
    menu_data = response.json()
    print("API response successfully parsed!")
except json.JSONDecodeError:
    print("Error: Response is not valid JSON.")
    exit()

# Initialize a calendar
calendar = Calendar()
event_count = 0  # Track the number of events created

# Navigate through JSON structure
for session in menu_data.get("FamilyMenuSessions", []):
    if session.get("ServingSession") == "Lunch":  # Only Lunch session
        print("Found Lunch session!")

        for menu_plan in session.get("MenuPlans", []):
            menu_plan_name = menu_plan.get("MenuPlanName", "")
            
            if menu_plan_name.startswith("Lunch"):  # Filter MenuPlanName
                print(f"Processing menu plan: {menu_plan_name}")

                for day in menu_plan.get("Days", []):
                    date_str = day.get("Date")
                    print(f"  Processing date: {date_str}")

                    try:
                        date = datetime.strptime(date_str, '%m/%d/%Y').date()  # Adjust date format
                    except ValueError:
                        print(f"  Error parsing date: {date_str}. Skipping...")
                        continue

                    lunch_items = []

                    for meal in day.get("MenuMeals", []):
                        for category in meal.get("RecipeCategories", []):
                            if category.get("CategoryName") == "Main Entree":  # Filter for "Main Entree"
                                for recipe in category.get("Recipes", []):
                                    recipe_name = recipe.get("RecipeName")
                                    if recipe_name:
                                        lunch_items.append(recipe_name)

                    print(f"    Main Entree items found: {', '.join(lunch_items) if lunch_items else 'None'}")

                    if lunch_items:
                        # Create an all-day event
                        event = Event()
                        event.name = "School Lunch - Main Entree"
                        event.begin = date  # All-day event (no specific time)
                        event.description = "\n".join(lunch_items)

                        # Add the event to the calendar
                        event.make_all_day()
                        calendar.events.add(event)
                        event_count += 1

# Save the calendar to an ICS file
ics_filename = "school_lunch_menu.ics"
with open(ics_filename, 'w') as f:
    f.writelines([line.replace('Z', '') for line in calendar.serialize_iter()])

print(f"ICS file generated: {ics_filename}")
print(f"Total events added: {event_count}")

