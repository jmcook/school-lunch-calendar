import re
from datetime import datetime, timedelta

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