import json
import sys
import io
import csv
import re
from pydantic import BaseModel, Field, ValidationError, validator
from typing import Optional, List

class ItineraryEntry(BaseModel):
    day: str = Field(..., description="The day number, e.g., 'Day 1'")
    date: str = Field(..., description="The specific date for the day, e.g., 'July 17, 2025'")
    activity: str = Field(..., description="The main activity for this entry")
    description: Optional[str] = Field(None, description="A brief description of the activity")
    location: Optional[str] = Field(None, description="The location of the activity")
    cost: Optional[float] = Field(None, description="Estimated cost for the activity")
    travel_distance_to_location: Optional[float] = Field(None, alias="Travel Distance to Location", description="Travel time/distance to the activity. Empty if last activity of day/trip.")

    @validator('cost', pre=True)
    def parse_cost(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, (int, float)):
            return float(v)
        try:
            # Remove commas before converting to float
            return float(str(v).replace(',', ''))
        except ValueError:
            # Check for 'Variable' and return None
            if isinstance(v, str) and 'variable' in v.lower():
                return None
            raise ValueError("Cost must be a number.")

    @validator('travel_distance_to_location', pre=True)
    def parse_travel_distance(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, (int, float)):
            return float(v)
        
        s = str(v).lower()
        
        # Handle "min" or "minutes" travel time
        match_min = re.search(r'(\d[\d,.]*)\s*(?:min|minutes)', s)
        if match_min:
            return float(match_min.group(1).replace(',', ''))
        
        # Handle "hour travel time"
        match_hour = re.search(r'(\d[\d,.]*)\s*hour', s)
        if match_hour:
            return float(match_hour.group(1).replace(',', '')) * 60  # Convert hours to minutes
            
        # Fallback for just a number
        match_num = re.search(r'(\d[\d,.]*)', s)
        if match_num:
            return float(match_num.group(1).replace(',', ''))
            
        return None

def parse_itinerary_content(itinerary_content: str) -> List[ItineraryEntry]:
    itinerary_entries = []
    lines = itinerary_content.split('\n')
    current_day = None
    current_date = None

    day_pattern = re.compile(r"^(?:##|\*\*)\s*Day (\d+):\s*([A-Za-z]+\s+\d{1,2},\s+\d{4}):(.*)$")
    activity_line_start_pattern = re.compile(r"^\*\s*(.*)$")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        day_match = day_pattern.match(line)
        if day_match:
            current_day = f"Day {day_match.group(1)}"
            current_date = day_match.group(2).strip()
            continue

        if current_day and line.startswith('*'):
            activity_line_match = activity_line_start_pattern.match(line)
            if not activity_line_match:
                continue

            full_activity_text = activity_line_match.group(1).strip()
            
            activity = full_activity_text
            description = None
            location = None
            cost = None
            travel_distance = None

            # 1. Extract and remove travel distance from the end of the line
            travel_distance_extract_pattern = re.compile(r"\s*\(([^)]*(?:min|minute|hour|walk to|travel time)[^)]*)\)\s*$")
            travel_match = travel_distance_extract_pattern.search(activity)
            if travel_match:
                travel_distance = travel_match.group(1).strip()
                activity = activity[:travel_match.start()].strip()

            # 2. Extract and remove location
            location_extract_pattern = re.compile(r"\s*@\s*([^($]*?)(?=\s*(?:$|\$|\()) ")
            loc_match = location_extract_pattern.search(activity)
            if loc_match:
                location = loc_match.group(1).strip()
                activity = activity[:loc_match.start()].strip()

            # 3. Extract and remove cost
            cost_extract_pattern = re.compile(r"\s*\$([\d,.]+|[Vv]ariable)(?:\s*per person)?")
            cost_match = cost_extract_pattern.search(activity)
            if cost_match:
                cost = cost_match.group(1).strip()
                activity = activity[:cost_match.start()].strip()

            # 4. Extract and remove description from remaining parentheses
            descriptions = re.findall(r"\(([^)]*)\)", activity)
            if descriptions:
                description = " ".join(d.strip() for d in descriptions)
                activity = re.sub(r"\s*\([^)]*\)", "", activity).strip()

            # 5. The rest is the activity
            activity = activity.strip()

            data = {
                "day": current_day,
                "date": current_date,
                "activity": activity,
                "description": description,
                "location": location,
                "cost": cost,
                "travel_distance_to_location": travel_distance
            }
            
            try:
                entry = ItineraryEntry(**data)
                itinerary_entries.append(entry)
            except ValidationError as e:
                error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
                print(f"Validation Error for row: {line} - {error_details}", file=sys.stderr)
                itinerary_entries.append(ItineraryEntry(
                    day=current_day, date=current_date, activity=activity,
                    description="VALIDATION_ERROR", location=error_details,
                    cost=None, travel_distance_to_location=None
                ))
            except Exception as e:
                print(f"Unexpected error for row: {line} - {e}", file=sys.stderr)
                itinerary_entries.append(ItineraryEntry(
                    day=current_day, date=current_date, activity=activity,
                    description="VALIDATION_ERROR", location=f"Unexpected error: {e}",
                    cost=None, travel_distance_to_location=None
                ))
                
    return itinerary_entries

def generate_csv_from_itinerary_entries(itinerary_entries: List[ItineraryEntry]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    header = ["Day", "Date", "Activity", "Description", "Location", "Cost", "Travel Distance to Location"]
    writer.writerow(header)

    for entry in itinerary_entries:
        writer.writerow([
            entry.day,
            entry.date,
            entry.activity,
            entry.description if entry.description is not None else "",
            entry.location if entry.location is not None else "",
            f"{entry.cost:.2f}" if entry.cost is not None else "",
            str(entry.travel_distance_to_location) if entry.travel_distance_to_location is not None else ""
        ])
    return output.getvalue()

def get_itinerary_entries_from_state(state: dict) -> List[ItineraryEntry]:
    conversation_history = state.get("conversation_history", [])
    itinerary_content = None

    for message in conversation_history:
        if message.get("role") == "assistant" and "Day 1:" in message.get("content", ""):
            itinerary_content = message["content"]
            break
    
    if itinerary_content:
        return parse_itinerary_content(itinerary_content)
    else:
        return []

if __name__ == "__main__":
    # This block is for standalone testing/execution of the script
    # It will read from a JSON file and print CSV to stdout, similar to original behavior
    if len(sys.argv) != 2:
        print("Usage: python generate_csv_itinerary.py <path_to_json_file>", file=sys.stderr)
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    state = {}
    try:
        with open(json_file_path, 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON in file: {json_file_path}", file=sys.stderr)
        sys.exit(1)

    itinerary_entries = get_itinerary_entries_from_state(state)
    csv_output = generate_csv_from_itinerary_entries(itinerary_entries)
    print(csv_output, end='')