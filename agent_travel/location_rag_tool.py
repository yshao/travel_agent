import pandas as pd
from pydantic import BaseModel
from typing import Tuple, Optional
from datetime import datetime
import time
import math

class VerifiedLocation(BaseModel):
    original_input: str
    verified_name: str
    coordinates: Tuple[float, float]
    country: str
    region: str
    confidence_score: float
    api_source: str
    verification_timestamp: datetime

class LocationRAG:
    def __init__(self, api_key: str = "dummy_api_key"):
        self.api_key = api_key
        self.cache = {} # Simple in-memory cache
        self.rate_limit_delay = 0.1 # Simulate rate limiting

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371 # Radius of Earth in kilometers
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance_km = R * c
        return distance_km * 0.621371 # Convert to miles

    def _call_geocoding_api(self, location_string: str) -> Optional[dict]:
        """
        Simulates an API call to a geocoding service.
        In a real scenario, this would integrate with Google Places, OpenStreetMap, etc.
        """
        # print(f"Simulating API call for: {location_string}") # Removed print statement
        time.sleep(self.rate_limit_delay) # Simulate network delay and rate limiting

        # Dummy data for demonstration
        if "Colosseum" in location_string:
            return {"verified_name": "Colosseum, Rome, Italy", "lat": 41.8902, "lng": 12.4922, "country": "Italy", "region": "Lazio", "confidence": 0.98, "source": "Simulated Google Places"}
        elif "Vatican City" in location_string:
            return {"verified_name": "Vatican City", "lat": 41.9029, "lng": 12.4534, "country": "Vatican City", "region": "Vatican City", "confidence": 0.99, "source": "Simulated Google Places"}
        elif "Palatine Hill" in location_string:
            return {"verified_name": "Palatine Hill, Rome, Italy", "lat": 41.8890, "lng": 12.4922, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Pantheon" in location_string:
            return {"verified_name": "Pantheon, Rome, Italy", "lat": 41.8986, "lng": 12.4769, "country": "Italy", "region": "Lazio", "confidence": 0.97, "source": "Simulated OpenStreetMap"}
        elif "Trevi Fountain" in location_string:
            return {"verified_name": "Trevi Fountain, Rome, Italy", "lat": 41.9009, "lng": 12.4833, "country": "Italy", "region": "Lazio", "confidence": 0.96, "source": "Simulated MapBox"}
        elif "Trastevere" in location_string:
            return {"verified_name": "Trastevere, Rome, Italy", "lat": 41.8890, "lng": 12.4730, "country": "Italy", "region": "Lazio", "confidence": 0.95, "source": "Simulated Google Places"}
        elif "Ostia Antica" in location_string:
            return {"verified_name": "Ostia Antica, Rome, Italy", "lat": 41.7550, "lng": 12.2850, "country": "Italy", "region": "Lazio", "confidence": 0.94, "source": "Simulated OpenStreetMap"}
        elif "Fiumicino Airport" in location_string:
            return {"verified_name": "Fiumicino Airport (FCO), Rome, Italy", "lat": 41.8003, "lng": 12.2389, "country": "Italy", "region": "Lazio", "confidence": 0.99, "source": "Simulated Google Places"}
        elif "Hotel" in location_string:
            return {"verified_name": "Hotel in Rome, Italy", "lat": 41.9028, "lng": 12.4964, "country": "Italy", "region": "Lazio", "confidence": 0.80, "source": "Simulated Generic"}
        elif "Your Choice" in location_string:
            return {"verified_name": "User Specified Location, Rome, Italy", "lat": 41.9028, "lng": 12.4964, "country": "Italy", "region": "Lazio", "confidence": 0.70, "source": "Simulated Generic"}
        elif "Various Shops" in location_string:
            return {"verified_name": "Shopping Area, Rome, Italy", "lat": 41.8955, "lng": 12.4823, "country": "Italy", "region": "Lazio", "confidence": 0.85, "source": "Simulated Generic"}
        elif "Food stall" in location_string:
            return {"verified_name": "Food Stall Area, Rome, Italy", "lat": 41.8902, "lng": 12.4922, "country": "Italy", "region": "Lazio", "confidence": 0.80, "source": "Simulated Generic"}
        elif "Airbnb Experience" in location_string:
            return {"verified_name": "Cooking Class Location, Rome, Italy", "lat": 41.8955, "lng": 12.4823, "country": "Italy", "region": "Lazio", "confidence": 0.80, "source": "Simulated Generic"}
        elif "Campo de' Fiori Market" in location_string:
            return {"verified_name": "Campo de' Fiori Market, Rome, Italy", "lat": 41.8955, "lng": 12.4723, "country": "Italy", "region": "Lazio", "confidence": 0.95, "source": "Simulated Google Places"}
        elif "Various Trattorias" in location_string:
            return {"verified_name": "Trattoria Area, Trastevere, Rome, Italy", "lat": 41.8890, "lng": 12.4730, "country": "Italy", "region": "Lazio", "confidence": 0.85, "source": "Simulated Generic"}
        elif "Restaurant in Ostia Antica" in location_string:
            return {"verified_name": "Restaurant, Ostia Antica, Rome, Italy", "lat": 41.7550, "lng": 12.2850, "country": "Italy", "region": "Lazio", "confidence": 0.85, "source": "Simulated Generic"}
        elif "Trattoria Monti" in location_string:
            return {"verified_name": "Trattoria Monti, Rome, Italy", "lat": 41.8955, "lng": 12.4923, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Trattoria Da Enzo al 29" in location_string:
            return {"verified_name": "Trattoria Da Enzo al 29, Rome, Italy", "lat": 41.8890, "lng": 12.4730, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Pizzeria Romana Bio" in location_string:
            return {"verified_name": "Pizzeria Romana Bio, Rome, Italy", "lat": 41.9029, "lng": 12.4534, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Castel Sant'Angelo" in location_string:
            return {"verified_name": "Castel Sant'Angelo, Rome, Italy", "lat": 41.9029, "lng": 12.4660, "country": "Italy", "region": "Lazio", "confidence": 0.95, "source": "Simulated Google Places"}
        elif "Ponte Sisto & Gelateria del Viale" in location_string:
            return {"verified_name": "Ponte Sisto & Gelateria del Viale, Rome, Italy", "lat": 41.8900, "lng": 12.4680, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Armando al Pantheon" in location_string:
            return {"verified_name": "Armando al Pantheon, Rome, Italy", "lat": 41.8986, "lng": 12.4769, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Borghese Gallery & Gardens" in location_string:
            return {"verified_name": "Borghese Gallery & Gardens, Rome, Italy", "lat": 41.9080, "lng": 12.4910, "country": "Italy", "region": "Lazio", "confidence": 0.95, "source": "Simulated Google Places"}
        elif "La Pergola" in location_string:
            return {"verified_name": "La Pergola, Rome, Italy", "lat": 41.9080, "lng": 12.4910, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Appian Way" in location_string:
            return {"verified_name": "Appian Way, Rome, Italy", "lat": 41.8500, "lng": 12.5000, "country": "Italy", "region": "Lazio", "confidence": 0.95, "source": "Simulated Google Places"}
        elif "Catacombs of Callixtus or Domitilla" in location_string:
            return {"verified_name": "Catacombs, Rome, Italy", "lat": 41.8500, "lng": 12.5000, "country": "Italy", "region": "Lazio", "confidence": 0.90, "source": "Simulated Google Places"}
        elif "Wine Bar in Trastevere" in location_string:
            return {"verified_name": "Wine Bar, Trastevere, Rome, Italy", "lat": 41.8890, "lng": 12.4730, "country": "Italy", "region": "Lazio", "confidence": 0.85, "source": "Simulated Generic"}
        elif "Trastevere Neighborhood" in location_string:
            return {"verified_name": "Trastevere Neighborhood, Rome, Italy", "lat": 41.8890, "lng": 12.4730, "country": "Italy", "region": "Lazio", "confidence": 0.95, "source": "Simulated Google Places"}
        else:
            return None # Location not found or ambiguous

    def verify_location(self, location_string: str) -> VerifiedLocation:
        """
        Verifies and enriches a single location string using a simulated RAG approach.
        """
        if location_string in self.cache:
            # print(f"Retrieving from cache: {location_string}") # Removed print statement
            return self.cache[location_string]

        api_response = self._call_geocoding_api(location_string)

        if api_response:
            verified_location = VerifiedLocation(
                original_input=location_string,
                verified_name=api_response["verified_name"],
                coordinates=(api_response["lat"], api_response["lng"]),
                country=api_response["country"],
                region=api_response["region"],
                confidence_score=api_response["confidence"],
                api_source=api_response["source"],
                verification_timestamp=datetime.now()
            )
            self.cache[location_string] = verified_location
            return verified_location
        else:
            # Handle invalid or ambiguous locations
            # print(f"Warning: Could not verify or found ambiguous results for '{location_string}'") # Removed print statement
            return VerifiedLocation(
                original_input=location_string,
                verified_name="Unverified/Ambiguous",
                coordinates=(0.0, 0.0), # Default to 0,0 for unverified
                country="Unknown",
                region="Unknown",
                confidence_score=0.0,
                api_source="N/A",
                verification_timestamp=datetime.now()
            )

    def process_itinerary_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reads a DataFrame, extracts locations, verifies them, and returns a DataFrame
        with original and verified location data.
        """
        if 'Location' not in df.columns:
            # print("Error: 'Location' column not found in the CSV file.") # Removed print statement
            return df

        verified_locations_data = []
        for index, row in df.iterrows():
            location_string = row['Location']
            if pd.isna(location_string) or location_string.strip() == "":
                verified_locations_data.append(None)
                continue

            verified_loc = self.verify_location(location_string)
            verified_locations_data.append(verified_loc)

        df['Verified_Location_Data'] = verified_locations_data

        travel_distances = [None] * len(df)
        for i in range(len(df) - 1):
            current_loc = df.loc[i, 'Verified_Location_Data']
            next_loc = df.loc[i+1, 'Verified_Location_Data']

            if current_loc and next_loc and current_loc.coordinates != (0.0, 0.0) and next_loc.coordinates != (0.0, 0.0):
                dist = self._haversine_distance(
                    current_loc.coordinates[0], current_loc.coordinates[1],
                    next_loc.coordinates[0], next_loc.coordinates[1]
                )
                travel_distances[i] = round(dist, 2)
            else:
                travel_distances[i] = None # Cannot calculate distance if location is unverified or missing

        df['Calculated_Travel_Distance_Miles'] = travel_distances
        return df

def process_itinerary(csv_file_path: str) -> pd.DataFrame:
    """
    Processes an itinerary CSV, verifies locations, calculates travel distances,
    and returns the processed DataFrame.
    """
    rag_agent = LocationRAG()
    try:
        itinerary_df = pd.read_csv(csv_file_path).reset_index(drop=True)
        itinerary_df['Location'] = itinerary_df['Location'].fillna('')
        itinerary_df = rag_agent.process_itinerary_locations(itinerary_df)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
        return pd.DataFrame()
    return itinerary_df
