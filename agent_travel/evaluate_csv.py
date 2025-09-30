import csv
import io
import re
import json
from pydantic import ValidationError
from orchestrator import ItineraryEntry # Assuming ItineraryEntry is accessible
from datetime import datetime

def evaluate_csv_itinerary(csv_data: str):
    """
    Evaluates a CSV itinerary against the ItineraryEntry Pydantic model.
    Returns a dictionary with evaluation results.
    """
    reader = csv.reader(io.StringIO(csv_data))
    header = next(reader) # Skip header row

    valid_rows = 0
    invalid_rows = 0
    errors = []
    
    previous_day_num = 0
    previous_date = None

    rows_for_evaluation = list(reader) # Read all rows into a list to check last row

    for i, row in enumerate(rows_for_evaluation):
        row_num = i + 2 # Account for header and 0-based index

        if len(row) < 7:
            errors.append(f"Row {row_num}: Insufficient columns. Expected 7, got {len(row)}.")
            invalid_rows += 1
            continue

        row_dict = {
            "day": row[0],
            "date": row[1],
            "activity": row[2],
            "description": row[3] if len(row) > 3 else None,
            "location": row[4] if len(row) > 4 else None,
            "cost": row[5] if len(row) > 5 else None,
            "travel_distance_to_next_location": row[6] if len(row) > 6 else None,
        }
        
        try:
            entry = ItineraryEntry(**row_dict)
            valid_rows += 1

            # --- Guardrail Checks ---
            current_day_num = 0
            day_num_match = re.match(r"Day (\d+)", entry.day)
            if day_num_match:
                try:
                    current_day_num = int(day_num_match.group(1))
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid Day number format: {entry.day}. Expected 'Day X' where X is a number.")
            else:
                errors.append(f"Row {row_num}: Invalid Day format: {entry.day}. Expected 'Day X'.")
            if i > 0: # Only check sequence from the second row onwards
                if current_day_num != previous_day_num and current_day_num != previous_day_num + 1:
                    errors.append(f"Row {row_num}: Day sequence error. Expected Day {previous_day_num + 1} or {previous_day_num}, got {entry.day}.")

            try:
                current_date = datetime.strptime(entry.date, '%B %d, %Y')
                if previous_date and current_day_num == previous_day_num + 1 and (current_date - previous_date).days != 1:
                    errors.append(f"Row {row_num}: Date chronology error. Expected date to be one day after {previous_date.strftime('%B %d, %Y')}, got {entry.date}.")
                elif previous_date and current_day_num == previous_day_num and current_date != previous_date:
                    errors.append(f"Row {row_num}: Date mismatch for same day. Expected {previous_date.strftime('%B %d, %Y')}, got {entry.date}.")
                previous_date = current_date
            except ValueError:
                errors.append(f"Row {row_num}: Invalid date format: {entry.date}. Expected 'Month Day, Year'.")
            
            previous_day_num = current_day_num

            # Travel Distance to Next Location check for last activity of trip
            if i == len(rows_for_evaluation) - 1 and entry.travel_distance_to_next_location:
                errors.append(f"Row {row_num}: Travel Distance to Next Location should be empty for the last activity of the trip.")

        except ValidationError as e:
            invalid_rows += 1
            errors.append(f"Row {row_num} invalid: {e.errors()}")

    return {
        "total_rows": valid_rows + invalid_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "errors": errors
    }

if __name__ == "__main__":
    # Example Usage (replace with actual CSV data from your app)
    sample_csv_data = """
Day,Date,Activity,Description,Location,Cost,Travel Distance to Next Location
Day 1,July 17, 2025,Explore City,Walking tour of historical sites,,$50,15 min walk
Day 1,July 17, 2025,Dinner at Local Restaurant,Try local cuisine,Downtown,Variable,
Day 2,July 18, 2025,Visit Museum,Art and history exhibits,Museum District,$20,10 min walk
Day 2,July 18, 2025,Lunch at Cafe,Quick bite,Near Museum,$15,
Day 3,July 19, 2025,Hiking,Scenic trails,National Park,,
"""
    
    print("\n--- Running Sample CSV Evaluation ---")
    results = evaluate_csv_itinerary(sample_csv_data)
    print(json.dumps(results, indent=2))

    invalid_sample_csv_data = """
Day,Date,Activity,Description,Location,Cost,Travel Distance to Next Location
Day 1,July 17, 2025,Explore City,Walking tour of historical sites,,$50,15 min walk
Day 1,July 17, 2025,Dinner at Local Restaurant,Try local cuisine,Downtown,Variable,
Day 3,July 18, 2025,Visit Museum,Art and history exhibits,Museum District,$20,10 min walk
Day 2,July 17, 2025,Lunch at Cafe,Quick bite,Near Museum,$15,
"""
    print("\n--- Running Invalid Sample CSV Evaluation ---")
    results = evaluate_csv_itinerary(invalid_sample_csv_data)
    print(json.dumps(results, indent=2))
