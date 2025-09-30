from travel_planner_agent import TravelPlannerAgent
from airbnb_agent import AirbnbAgent
from budget_agent import BudgetAgent
from location_rag_tool import process_itinerary
from generate_csv_itinerary import generate_csv_itinerary
import json
import re
import os
import io
import sys
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import csv
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile
import streamlit as st


def call_gemini(prompt):
    print(f"\n-----PROMPT-----\n{prompt}\n--------------------\n")
    try:

        model_name = 'gemini-1.5-flash'
        print(f"Attempting to use model: {model_name}") # Debug print
        model = genai.GenerativeModel(model_name)
        if model is None:
            print("Error: Gemini GenerativeModel could not be initialized. Check API key and network.")
            return "Error: Gemini model not available."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"



TRIP_DATA_FILE = "user_trips.json"

class ItineraryEntry(BaseModel):
    day: str = Field(..., description="The day number, e.g., 'Day 1'")
    date: str = Field(..., description="The specific date for the day, e.g., 'July 17, 2025'")
    activity: str = Field(..., description="The main activity for this entry")
    description: Optional[str] = Field(None, description="A brief description of the activity")
    location: Optional[str] = Field(None, description="The location of the activity")
    cost: Optional[float] = Field(None, description="Estimated cost for the activity")
    travel_distance_to_next_location: Optional[float] = Field(None, alias="Travel Distance to Next Location", description="Travel time/distance to the next activity. Empty if last activity of day/trip.")



class Orchestrator:
    def __init__(self):
        # Load .env for local development (ignored in Docker/HF Spaces)
        load_dotenv()

        # Get API key from environment (works for both local .env and HF Spaces secrets)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            print(f"Gemini API key loaded: {bool(gemini_api_key)}") # Debug print
        else:
            error_msg = "⚠️ GEMINI_API_KEY not found. For HF Spaces: Add it in Settings → Repository secrets"
            print(error_msg)
            # Display error in Streamlit if available
            try:
                st.error(error_msg)
            except:
                pass
        self.travel_planner_agent = TravelPlannerAgent()
        self.airbnb_agent = AirbnbAgent()

    @st.cache_data
    def _read_all_trips(_self):
        if not os.path.exists(TRIP_DATA_FILE) or os.path.getsize(TRIP_DATA_FILE) == 0:
            return {}
        with open(TRIP_DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _write_all_trips(_self, all_trips):
        # Invalidate cache when writing
        _self._read_all_trips.clear()
        _self.get_all_trip_titles.clear()
        with open(TRIP_DATA_FILE, "w") as f:
            json.dump(all_trips, f, indent=4)

    @st.cache_data
    def get_all_trip_titles(_self):
        return list(_self._read_all_trips().keys())

    def save_trip_data(self, trip_title, state_to_save):
        all_trips = self._read_all_trips()
        all_trips[trip_title] = state_to_save
        self._write_all_trips(all_trips)

    def load_trip_data(self, trip_title):
        all_trips = self._read_all_trips()
        return all_trips.get(trip_title)

    def generate_pdf_itinerary(self, state):
        state = json.loads(state)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Travel Itinerary", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        # Extract itinerary from conversation history
        itinerary_text = ""
        for entry in state["conversation_history"]:
            if entry["role"] == "assistant" and "Day 1:" in entry["content"]: # Simple heuristic to find itinerary
                itinerary_text = entry["content"]
                break
        
        if itinerary_text:
            for line in itinerary_text.split('\n'):
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("No itinerary found in conversation history.", styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_csv_itinerary(self, state):
        state = json.loads(state)
        return generate_csv_itinerary(state)

    def validate_csv_itinerary(self, csv_data):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_file_input:
            temp_file_input.write(csv_data)
            temp_file_path_input = temp_file_input.name

        try:
            processed_df = process_itinerary(temp_file_path_input)
            
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_file_processed:
                processed_df.to_csv(temp_file_processed.name, index=False)
                temp_file_path_processed = temp_file_processed.name

            agent = BudgetAgent(temp_file_path_processed)
            agent.load_data()
            agent.validate_data()
            summary = agent.get_summary()

            os.remove(temp_file_path_processed)
            return summary
        finally:
            os.remove(temp_file_path_input)

    def get_default_state(self):
        return {
            "current_phase": "INITIAL",
            "plan": {
                "destination": None,
                "duration": None,
                "month": None,
                "traveler_type": None,
                "interests": [],
                "budget": None,
            },
            "conversation_history": []
        }

    def generate_trip_title_with_llm(self, plan, initial_query=None):
        if initial_query:
            prompt = f"""
            Generate a concise and descriptive title for a trip based on the following user query:
            '{initial_query}'

            Return only the title, without any additional text or punctuation.
            """
        else:
            prompt = f"""
            Generate a concise and descriptive title for a trip based on the following details:
            Destination: {plan.get("destination")}
            Duration: {plan.get("duration")} days
            Month: {plan.get("month")}
            Traveler Type: {plan.get("traveler_type")}
            Interests: {', '.join(plan.get("interests", []))}
            Budget: ${plan.get("budget")}

            Return only the title, without any additional text or punctuation.
            """
        title = call_gemini(prompt).strip()
        # Clean up any potential quotes or extra characters from LLM response
        title = title.replace('"', '').replace("'", '').strip()
        return title if title else "Untitled Trip"

    def save_current_trip(self, trip_title, current_state):
        if not trip_title:
            initial_query = current_state["plan"].get("initial_query")
            trip_title = self.generate_trip_title_with_llm(current_state["plan"], initial_query=initial_query)
            current_state["conversation_history"].append({"role": "assistant", "content": f"No title provided. Auto-generating title: {trip_title}"})

        self.save_trip_data(trip_title, current_state)
        current_state["conversation_history"].append({"role": "assistant", "content": f"Trip saved successfully with title: {trip_title}"})
        return current_state

    def load_saved_trip(self, trip_title, current_state):
        loaded_state = self.load_trip_data(trip_title)
        if loaded_state:
            return loaded_state
        else:
            current_state["conversation_history"].append({"role": "assistant", "content": f"No trip found with title: {trip_title}."})
            return current_state

    def process_user_input(self, user_input, current_state):
        state = current_state
        ai_response = ""

        state["conversation_history"].append({"role": "user", "content": user_input})

        if state["current_phase"] == "INITIAL":
            state["plan"]["initial_query"] = user_input # Store the initial query
            self.travel_planner_agent.parse_with_llm(user_input, state["plan"])
            missing_info = self.travel_planner_agent.check_missing_info(state["plan"])

            if not missing_info:
                state["current_phase"] = "ITINERARY"
                confirmation_message = "**Understood Parameters:**\n"
                for key, value in state["plan"].items():
                    if value:
                        confirmation_message += f"- {key.replace('_', ' ').title()}: {value}\n"
                confirmation_message += "\nParameters confirmed! Generating high-level itinerary..."
                state["conversation_history"].append({"role": "assistant", "content": confirmation_message})

                prompt = f"""Generate a {state['plan']['duration']}-day itinerary for a trip to {state['plan']['destination']} in {state['plan']['month']} for {state['plan']['traveler_type']} interested in {', '.join(state['plan']['interests'])}. The budget is around ${state['plan']['budget']}. For each day, include a specific date (e.g., July 17, 2025). Focus on the following format as described in PROMPT.md: ## X-Day [Destination] Itinerary ([Interests] Focus)

For each activity, include: Activity Name (Description) @ Location $Cost (Travel Distance to Next Location). Leave Travel Distance empty for the last activity of the day or trip.

**Day 1: [Date]: ...**
* ...

**Day 2: [Date]: ...**
* ...

Type 'details [Day X]' or 'details [attraction name]' for more information, or 'budget estimate' to see a cost breakdown."""
                ai_response = call_gemini(prompt)
                state["conversation_history"].append({"role": "assistant", "content": """
Type 'details [Day X]' or 'details [attraction name]' for more information, 'budget estimate' to see a cost breakdown, or 'find airbnb' for accommodation suggestions."""})
            else:
                ai_response = "**Understood Parameters:**\n"
                for key, value in state["plan"].items():
                    if value:
                        ai_response += f"- {key.replace('_', ' ').title()}: {value}\n"
                
                ai_response += "\nTo generate a travel plan, I need a bit more information. Please provide the following:\n"
                for item in missing_info:
                    ai_response += f"- {item.title()}\n"

        elif state["current_phase"] == "ITINERARY":
            if user_input.lower().startswith("details"):
                detail_query = user_input.replace("details ", "").strip()
                prompt = f"Provide practical details for '{detail_query}' from the itinerary for a trip to {state['plan']['destination']}. Include estimated time, brief description (text only), exact address/real-world location (if applicable), estimated cost (if applicable), suggestions for nearby attractions or food, and relevant Google Search queries or direct browsing links for booking. Focus on the format as described in PROMPT.md."
                ai_response = call_gemini(prompt)

            elif user_input.lower() == "budget estimate":
                state["current_phase"] = "BUDGET"
                prompt = f"Provide a rough budget breakdown and optimization tips for a {state['plan']['duration']}-day trip to {state['plan']['destination']} with a budget of ${state['plan']['budget']}. Break down costs for flights, accommodation, food and activities. Suggest ways to optimize the budget. Focus on the format as described in PROMPT.md."
                ai_response = call_gemini(prompt)
            elif user_input.lower() == "find airbnb":
                ai_response = self.airbnb_agent.find_optimal_airbnb(state["plan"])
            elif user_input.lower() == "generate csv":
                ai_response = self.generate_csv_itinerary(json.dumps(state))
            else:
                ai_response = "Type 'details [Day X]', 'budget estimate', 'find airbnb', or 'generate csv'."
        
        elif state["current_phase"] == "BUDGET":
            if user_input.lower() == "new plan":
                state = self.get_default_state() # Reset state
                ai_response = "Ready for a new travel plan."
            else:
                ai_response = "What else can I help you with, or would you like to start a 'new plan'?'"
        
        if ai_response:
            state["conversation_history"].append({"role": "assistant", "content": ai_response})
        
        return state
