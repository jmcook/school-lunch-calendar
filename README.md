# school-lunch-calendar
LinqConnect / Titan School Lunch Menu to Google Calendar

## Overview
This script fetches school lunch menus from the LinqConnect API for a specified date range and exports them as a `.ics` calendar file. The generated file can be imported into Google Calendar or other calendar applications for easy tracking of school meal schedules.

## Features
- ✅ **Command-line date support**: Specify custom date ranges using `--start-date` and `--end-date` parameters.
- 🍱 **Lunch session filtering**: Only processes "Lunch" sessions and "Main Entree" items.
- 📅 **Descriptive event names**: Events include the date and meal type (e.g., "School Lunch - Main Entree (2025-06-02: Chicken, Rice)").
- 📥 **ICS file output**: Generates a `school_lunch_menu.ics` file for easy import into calendar apps.

## Installation
1. **Python 3**: Ensure Python 3 is installed on your system.
2. **Install dependencies**:
   ```bash
   pip install requests ics pytz
   ```

## Usage
Run the script with the `--start-date` and `--end-date` parameters in `MM-DD-YYYY` format:

