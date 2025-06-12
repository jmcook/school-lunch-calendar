#!python3

import argparse
import requests
from ics import Calendar, Event
from datetime import datetime
import json
import pytz

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Fetch school lunch menu from LinqConnect and generate ICS calendar.")
parser.add_argument("--start-date", required=True, help="Start date in MM-DD-YYYY format (e.g., 06-02-2025)")
parser.add_argument("--end-date", required=True, help="End date in MM-DD-YYYY format (e.g., 06-13-2025)")
args = parser.parse_args()

# User-defined variables from command line
start_date = args.start_date
end_date = args.end_date
building_id = "816d4352-8ada-eb11-a2c4-babb11d0075f"  # Change as needed
district_id = "c48c6d9c-9ad9-eb11-a2c4-ae34736f1064"  # Change as needed

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
            
            if menu_plan_name.startswith("Lunch- Elementary"):  # Filter MenuPlanName
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
                        event.name = f"School Lunch - Main Entree ({date.strftime('%Y-%m-%d')}: {', '.join(lunch_items)})"
                        event.begin = date  # All-day event (no specific time)
                        event.description = "Lunch"  # Only include meal type in description

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
