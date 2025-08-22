#!python3

import requests
from ics import Calendar, Event
from datetime import datetime
import json
import pytz

import argparse
import re
from datetime import datetime, timedelta

# Parse command line arguments
parser = argparse.ArgumentParser(description='Fetch school lunch menu from LinqConnect API and generate ICS calendar file.')
parser.add_argument('--start-date', required=True, help='Start date in MM-DD-YYYY format or relative duration (e.g., 1m, 2w, 5d)')
parser.add_argument('--end-date', required=True, help='End date in MM-DD-YYYY format or relative duration (e.g., 1m, 2w, 5d)')
parser.add_argument('--building-id', required=True, help='Building ID for the school')
parser.add_argument('--district-id', required=True, help='District ID for the school')
args = parser.parse_args()


def parse_date_range(start_date_str, end_date_str):
    """
    Parse date range from command line arguments.
    Supports MM-DD-YYYY format and relative durations (1m, 2w, 5d).
    """
    today = datetime.now().date()
    
    # Check if start_date is a relative duration
    if re.match(r'^\d+[dwmy]$', start_date_str.lower()):
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
    
    # Check if end_date is a relative duration
    elif re.match(r'^\d+[dwmy]$', end_date_str.lower()):
        # Parse start_date as MM-DD-YYYY
        start_date = datetime.strptime(start_date_str, '%m-%d-%Y').date()
        
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
    
    # Both dates are in MM-DD-YYYY format
    return start_date_str, end_date_str

# Parse and validate date range
start_date, end_date = parse_date_range(args.start_date, args.end_date)

# Use other command line arguments
building_id = args.building_id
district_id = args.district_id

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

