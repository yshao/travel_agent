class AirbnbAgent:
    def __init__(self):
        pass

    def find_optimal_airbnb(self, plan):
        destination = plan.get("destination", "")
        budget = plan.get("budget", "a reasonable budget")
        traveler_type = plan.get("traveler_type", "travelers")
        interests = ", ".join(plan.get("interests", []))

        response = f"Searching for optimal Airbnb locations in {destination} for {traveler_type} with {interests} interests, within {budget}.\n\n"
        response += "Please note: This tool provides *suggestions* for optimal Airbnb locations and does not handle actual booking or scheduling. You would need to visit Airbnb or other booking platforms to make reservations.\n\n"
        response += "Based on your preferences, here are some highly-rated neighborhoods/areas and example Airbnbs:\n"
        response += "- **Area 1: [Neighborhood Name]** (e.g., close to attractions, good nightlife)\n"
        response += "  - *Example Airbnb:* 'Cozy apartment near [Landmark]' - [Link to Airbnb] (Est. ${price}/night)\n"
        response += "- **Area 2: [Another Neighborhood]** (e.g., quieter, family-friendly, good food scene)\n"
        response += "  - *Example Airbnb:* 'Spacious loft with city views' - [Link to Airbnb] (Est. ${price}/night)\n"
        response += "\nConsider these options and let me know if you'd like more details on a specific area or type of accommodation!"
        return response