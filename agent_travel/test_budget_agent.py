import unittest
import pandas as pd
import os
from budget_agent import BudgetAgent, Trip

class TestBudgetAgent(unittest.TestCase):

    def setUp(self):
        # Create a dummy CSV for testing
        data = {
            'Day': [1, 1, 2, 3, 3, 4],
            'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-03', '2024-01-02'],
            'Activity': ['Museum', 'Lunch', 'Train', 'Hotel', 'Dinner', 'Sightseeing'],
            'Cost': ['$20', '$15', '$50', '$150', 'invalid', '$25'],
            'Travel Distance to Next Location': ['', '', '', '', '', ''],
            'Description': ['', '', '', '', '', '']
        }
        self.csv_path = 'test_trip.csv'
        pd.DataFrame(data, dtype=object).to_csv(self.csv_path, index=False)

        # Create a valid CSV for summary testing
        data = {
            'Day': [1, 1, 2],
            'Date': ['2024-01-01', '2024-01-01', '2024-01-02'],
            'Activity': ['Museum', 'Lunch', 'Train'],
            'Cost': ['20', '15', '50'],
            'Travel Distance to Next Location': [None, None, None],
            'Description': [None, None, None]
        }
        self.valid_csv_path = 'valid_trip.csv'
        pd.DataFrame(data, dtype=object).to_csv(self.valid_csv_path, index=False)


    def tearDown(self):
        # Clean up the dummy CSV files
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        if os.path.exists(self.valid_csv_path):
            os.remove(self.valid_csv_path)

    def test_load_data(self):
        agent = BudgetAgent(self.csv_path)
        agent.load_data()
        self.assertEqual(len(agent.trips), 5)
        self.assertEqual(len(agent.errors), 1)

    def test_validation(self):
        agent = BudgetAgent(self.csv_path)
        agent.load_data()
        agent.validate_data()
        self.assertIn("Date sequence is not in chronological order.", agent.errors)

    def test_summary(self):
        agent = BudgetAgent(self.valid_csv_path)
        agent.load_data()
        agent.validate_data()
        summary = agent.get_summary()
        self.assertNotIn('errors', summary)
        self.assertIn(1, summary)
        self.assertIn(2, summary)
        self.assertEqual(summary[1]['total_cost'], 35)
        self.assertEqual(summary[2]['total_cost'], 50)

if __name__ == '__main__':
    unittest.main()