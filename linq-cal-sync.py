#!python3

import argparse
import requests
from ics import Calendar, Event
from datetime import datetime
import json
import pytz
from typing import Optional, Dict, Any, List

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch school lunch menu from LinqConnect and generate ICS calendar.")
    parser.add_argument("--start-date", required=True, help="Start date in MM-DD-YYYY format (e.g., 06-02-2025)")
    parser.add_argument("--end-date", required=True, help="End date in MM-DD-YYYY format (e.g., 06-13-2025)")
    return parser.parse_args()

def validate_date(date_str: str) -> Optional[datetime.date]:
    """Validate and parse a date string in MM-DD-YYYY format."""
    try:
        return datetime.strptime(date_str, '%m-%d-%Y').date()
    except ValueError:
        print(f"Invalid date format: {date_str}. Please use MM-DD-YYYY format.")
        return None

def fetch_lunch_menu(
    building_id: str,
    district_id: str,
    start_date: str,
    end_date: str
) -> Optional[Dict[str, Any]]:
    """Fetch lunch menu data from LinqConnect API."""
    api_url = f"https://api.linqconnect.com/api/FamilyMenu?buildingId={building_id}&districtId={district_id}&startDate={start_date}&endDate={end_date}"
    
    try:
        print("Fetching data from API...")
        response = requests.get(api_url)
        
        if response.status_code != 200:
            print(f"Error fetching data! HTTP Status Code: {response.status_code}")
            print("Response Text:", response.text)
            return None

        try:
            menu_data = response.json()
            print("API response successfully parsed!")
            return menu_data
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON.")
            return None

    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None

def process_menu_data(menu_data: Dict[str, Any]) -> List[Event]:
    """Process menu data and create calendar events."""
    events = []
    event_count = 0
    
    # Define US Eastern Timezone
    eastern_tz = pytz.timezone("America/New_York")
    
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

                        # Validate and parse date
                        date = validate_date(date_str)
                        if not date:
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
                            events.append(event)
                            event_count += 1

    print(f"Total events created: {event_count}")
    return events

def main():
    """Main function to run the script."""
    args = parse_arguments()
    
    # Validate dates
    start_date = validate_date(args.start_date)
    end_date = validate_date(args.end_date)
    
    if not start_date or not end_date:
        return
    
    # User-defined variables
    building_id = "816d4352-8ada-eb11-a2c4-babb11d0075f"  # Change as needed
    district_id = "c48c6d9c-9ad9-eb11-a2c4-ae34736f1064"  # Change as needed
    
    # Fetch lunch menu data
    menu_data = fetch_lunch_menu(building_id, district_id, args.start_date, args.end_date)
    
    if not menu_data:
        return
    
    # Process menu data and create events
    events = process_menu_data(menu_data)
    
    # Create calendar
    calendar = Calendar()
    calendar.events = events
    
    # Save the calendar to an ICS file
    ics_filename = "school_lunch_menu.ics"
    with open(ics_filename, 'w') as f:
        f.writelines([line.replace('Z', '') for line in calendar.serialize_iter()])
    
    print(f"ICS file generated: {ics_filename}")
    print(f"Total events added: {len(events)}")

if __name__ == "__main__":
    main()
