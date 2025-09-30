import unittest
import json
import sys
import os
import io
from unittest.mock import patch, mock_open
from generate_csv_itinerary import parse_itinerary_content, generate_csv_from_itinerary_entries, ItineraryEntry

class TestGenerateCsvItinerary(unittest.TestCase):

    def setUp(self):
        self.test_json_path = "/tmp/test_state.json"
        self.maxDiff = None

    def tearDown(self):
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)

    def _create_test_json(self, content):
        with open(self.test_json_path, "w") as f:
            json.dump(content, f)

    def test_parse_valid_itinerary(self):
        itinerary_content = """
**Day 1: July 20, 2025:**
* Colosseum Tour (Includes underground and arena floor access) @ Colosseum $75.00 (2.5)
* Roman Forum & Palatine Hill (Explore the ancient ruins) @ Roman Forum $30.00
**Day 2: July 21, 2025:**
* Vatican Museums & Sistine Chapel (Skip-the-line access) @ Vatican City $50.00 (1.0)
* St. Peter's Basilica (Climb to the dome for panoramic views) @ Vatican City $0.00
"""
        parsed_entries = parse_itinerary_content(itinerary_content)
        
        self.assertEqual(len(parsed_entries), 4)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Colosseum Tour', description='Includes underground and arena floor access', location='Colosseum', cost=75.0, travel_distance_to_location=2.5))
        self.assertEqual(parsed_entries[1], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Roman Forum & Palatine Hill', description='Explore the ancient ruins', location='Roman Forum', cost=30.0, travel_distance_to_location=None))
        self.assertEqual(parsed_entries[2], ItineraryEntry(day='Day 2', date='July 21, 2025', activity='Vatican Museums & Sistine Chapel', description='Skip-the-line access', location='Vatican City', cost=50.0, travel_distance_to_location=1.0))
        self.assertEqual(parsed_entries[3], ItineraryEntry(day='Day 2', date='July 21, 2025', activity='St. Peter\'s Basilica', description='Climb to the dome for panoramic views', location='Vatican City', cost=0.0, travel_distance_to_location=None))

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_generate_csv_from_valid_itinerary(self, mock_stderr, mock_stdout):
        itinerary_content = """
**Day 1: July 20, 2025:**
* Colosseum Tour (Includes underground and arena floor access) @ Colosseum $75.00 (2.5)
* Roman Forum & Palatine Hill (Explore the ancient ruins) @ Roman Forum $30.00
"""
        parsed_entries = parse_itinerary_content(itinerary_content)
        csv_output = generate_csv_from_itinerary_entries(parsed_entries)
        
        expected_csv = """Day,Date,Activity,Description,Location,Cost,Travel Distance to Location
Day 1,"July 20, 2025",Colosseum Tour,Includes underground and arena floor access,Colosseum,75.00,2.5
Day 1,"July 20, 2025",Roman Forum & Palatine Hill,Explore the ancient ruins,Roman Forum,30.00,
"""
        self.assertEqual(csv_output, expected_csv)
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_no_itinerary_found(self, mock_stderr, mock_stdout):
        itinerary_content = "I can help you with that, but I need more details."
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 0)
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_validation_error_invalid_cost(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity with invalid cost @ Location $abc"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0].cost, None)
        self.assertIn("cost: Invalid cost format", parsed_entries[0].description)
        self.assertIn("Validation Error for row: * Activity with invalid cost @ Location $abc - cost: Invalid cost format", mock_stderr.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_missing_optional_fields(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Simple Activity"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Simple Activity', description=None, location=None, cost=None, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_only_description(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity (Description only)"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description='Description only', location=None, cost=None, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_only_location(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity @ Location"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description=None, location='Location', cost=None, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_only_cost(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity $10.50"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description=None, location=None, cost=10.50, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_only_travel_distance(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity (3.0)"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description=None, location=None, cost=None, travel_distance_to_location=3.0))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_comma_in_description(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity (Description, with comma) @ Location $10.00 (1.0)"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description='Description, with comma', location='Location', cost=10.00, travel_distance_to_location=1.0))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_dollar_sign_in_description(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity (Description $ with dollar) @ Location $10.00 (1.0)"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description='Description $ with dollar', location='Location', cost=10.00, travel_distance_to_location=1.0))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_commas_in_cost(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity @ Location $1,234.56"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity', description=None, location='Location', cost=1234.56, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_activity_with_no_space_after_asterisk(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n*Activity Name"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='July 20, 2025', activity='Activity Name', description=None, location=None, cost=None, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_multiple_days_and_activities(self, mock_stderr, mock_stdout):
        itinerary_content = (
            "**Day 1: Jan 01, 2025:**\n"
            "* Activity A (Desc A) @ Loc A $10.00 (1.0)\n"
            "* Activity B (Desc B) @ Loc B $20.00\n"
            "**Day 2: Jan 02, 2025:**\n"
            "* Activity C @ Loc C $30.00 (2.0)\n"
            "* Activity D\n"
        )
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 4)
        self.assertEqual(parsed_entries[0], ItineraryEntry(day='Day 1', date='Jan 01, 2025', activity='Activity A', description='Desc A', location='Loc A', cost=10.00, travel_distance_to_location=1.0))
        self.assertEqual(parsed_entries[1], ItineraryEntry(day='Day 1', date='Jan 01, 2025', activity='Activity B', description='Desc B', location='Loc B', cost=20.00, travel_distance_to_location=None))
        self.assertEqual(parsed_entries[2], ItineraryEntry(day='Day 2', date='Jan 02, 2025', activity='Activity C', description=None, location='Loc C', cost=30.00, travel_distance_to_location=2.0))
        self.assertEqual(parsed_entries[3], ItineraryEntry(day='Day 2', date='Jan 02, 2025', activity='Activity D', description=None, location=None, cost=None, travel_distance_to_location=None))
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_travel_distance_min(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity (30 min travel time)"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0].travel_distance_to_location, 30.0)
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_travel_distance_hour(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity (1 hour travel time)"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0].travel_distance_to_location, 60.0)
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_cost_per_person(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity $60 per person"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0].cost, 60.0)
        self.assertEqual(mock_stderr.getvalue(), "")

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_parse_cost_with_comma(self, mock_stderr, mock_stdout):
        itinerary_content = "**Day 1: July 20, 2025:**\n* Activity $1,234.56"
        parsed_entries = parse_itinerary_content(itinerary_content)
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0].cost, 1234.56)
        self.assertEqual(mock_stderr.getvalue(), "")