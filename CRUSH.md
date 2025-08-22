# CRUSH.md
#
# This file helps agentic coding assistants (like me!) operate effectively in this codebase.
# I will use this file to learn about:
# - Build/lint/test commands
# - Code style preferences
# - Project structure and organization

## Commands

# Run script with absolute dates
python linq-cal-sync.py --start-date 08-21-2025 --end-date 08-28-2025 --building-id 816d4352-8ada-eb11-a2c4-babb11d0075f --district-id c48c6d9c-9ad9-eb11-a2c4-ae34736f1064

# Run script with relative duration from today (e.g., 1 month)
python linq-cal-sync.py --start-date 1m --end-date 1m --building-id 816d4352-8ada-eb11-a2c4-babb11d0075f --district-id c48c6d9c-9ad9-eb11-a2c4-ae34736f1064

# Run script with start date and relative duration
python linq-cal-sync.py --start-date 08-21-2025 --end-date 2w --building-id 816d4352-8ada-eb11-a2c4-babb11d0075f --district-id c48c6d9c-9ad9-eb11-a2c4-ae34736f1064

# Run with special date values
python linq-cal-sync.py --start-date today --end-date tomorrow --building-id 816d4352-8ada-eb11-a2c4-babb11d0075f --district-id c48c6d9c-9ad9-eb11-a2c4-ae34736f1064

# Run with custom config file
python linq-cal-sync.py --config my_config.yaml

# Install dependencies
pip install requests ics pytz

# Install PyYAML for config file support
pip install pyyaml

## Style Guide

# General
- Python 3
- Use requests, ics, pytz libraries
- Prefer descriptive variable names
- Add comments for complex logic

# Imports
- Standard library imports first
- Third-party imports after standard library
- One import per line

# Error Handling
- Check HTTP status codes
- Handle JSON decode errors
- Parse dates with try/except

# Formatting
- 4 space indentation
- Max line length 88 characters
- Use f-strings for string formatting
- Use .format() or join() for dynamic strings in logs

# Naming
- Use snake_case for variables and functions
- Use CAP_SNAKE_CASE for constants

# Best Practices
- Validate API responses
- Filter data early (session, category)
- Use context managers for file operations
- Make events all-day with proper timezone handling