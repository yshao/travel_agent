import json
import re
import os
import datetime
from gemini_utils import call_gemini

class TravelPlannerAgent:
    def __init__(self):
        pass

    

    def parse_with_llm(self, user_input, current_plan):
        prompt = f"""
        Extract the following travel planning parameters from the user's input. 
        Return the information as a JSON object with the keys: 
        'destination', 'duration', 'month', 'traveler_type', 'interests', 'budget'.
        If a value is not present, set it to null.

        User Input: '{user_input}'
        """
        response_text = call_gemini(prompt)
        
        try:
            json_match = re.search(r"```json\n([\s\S]*?)\n```", response_text)
            if json_match:
                json_str = json_match.group(1)
                extracted_data = json.loads(json_str)
            else:
                extracted_data = json.loads(response_text) # Try parsing directly if no code block

            for key, value in extracted_data.items():
                if value is not None:
                    current_plan[key] = value
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing LLM response: {e}")
            pass

    def check_missing_info(self, plan):
        missing = []
        if not plan["destination"]:
            missing.append("destination")
        if not plan["duration"]:
            missing.append("duration")
        if not plan["month"]:
            missing.append("month")
        if not plan["traveler_type"]:
            missing.append("traveler type")
        if not plan["interests"]:
            missing.append("interests")
        if not plan["budget"]:
            missing.append("budget")
        return missing

