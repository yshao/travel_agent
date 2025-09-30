
import pandas as pd
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import numpy as np

class Trip(BaseModel):
    """A Pydantic model to represent a trip record from a CSV file."""
    day: Optional[int] = Field(None, alias='Day')
    date: Optional[str] = Field(None, alias='Date')
    activity: Optional[str] = Field(None, alias='Activity')
    description: Optional[str] = Field(None, alias='Description')
    location: Optional[str] = Field(None, alias='Location')
    cost: Optional[str] = Field(None, alias='Cost')
    travel_distance_to_next_location: Optional[float] = Field(None, alias='Travel Distance to Next Location')

    @validator('cost')
    def validate_cost(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = v.replace('$', '').replace(',', '')
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError("Invalid cost format")

class BudgetAgent:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.trips: List[Trip] = []
        self.errors = []

    def load_data(self):
        try:
            df = pd.read_csv(self.csv_path, dtype={'Cost': str, 'Description': str, 'Travel Distance to Next Location': str})

            if 'Day' not in df.columns or df['Day'].isnull().all():
                # Programmatically add Day and Date
                num_activities = len(df)
                activities_per_day = 4 
                num_days = (num_activities + activities_per_day - 1) // activities_per_day
                
                days = []
                for i in range(num_days):
                    days.extend([i + 1] * activities_per_day)
                df['Day'] = days[:num_activities]

                start_date = datetime(2025, 7, 20)
                dates = []
                for i in range(num_days):
                    date = start_date + pd.Timedelta(days=i)
                    dates.extend([date.strftime('%Y-%m-%d')] * activities_per_day)
                df['Date'] = dates[:num_activities]


            df['Travel Distance to Next Location'] = df['Travel Distance to Next Location'].replace({np.nan: None})
            df['Description'] = df['Description'].replace({np.nan: None})
            df['Day'] = pd.to_numeric(df['Day'], errors='coerce').astype(pd.Int64Dtype())

            # Forward fill Day and Date
            df['Day'] = df['Day'].ffill()
            df['Date'] = df['Date'].ffill()
            
            # Drop rows where essential information is missing
            df.dropna(subset=['Activity', 'Cost'], inplace=True)

            for index, row in df.iterrows():
                try:
                    self.trips.append(Trip(**row.to_dict()))
                except ValueError as e:
                    self.errors.append(f"Row {index + 2}: {e}")
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.csv_path}")
        except Exception as e:
            self.errors.append(f"An error occurred: {e}")

    def validate_data(self):
        if not self.trips:
            return

        # Validate day and date sequences
        days = [trip.day for trip in self.trips if trip.day is not None]
        dates = [trip.date for trip in self.trips if trip.date is not None]

        if sorted(days) != days:
            self.errors.append("Day sequence is not in ascending order.")
        
        # Date validation
        date_objects = []
        for i, date_str in enumerate(dates):
            try:
                # Attempt to parse multiple date formats
                dt = None
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                if dt is None:
                    raise ValueError
                date_objects.append(dt)
            except (ValueError, TypeError):
                self.errors.append(f"Invalid date format at index {i}: {date_str}")

        if sorted(date_objects) != date_objects:
            self.errors.append("Date sequence is not in chronological order.")

    def get_summary(self):
        if self.errors:
            return {"errors": self.errors}
        
        summary = {}
        for trip in self.trips:
            if trip.day is not None:
                if trip.day not in summary:
                    summary[trip.day] = {"date": trip.date, "activities": [], "total_cost": 0}
                summary[trip.day]["activities"].append(f"{trip.activity}: ${trip.cost}")
                summary[trip.day]["total_cost"] += trip.cost
        
        return summary

if __name__ == '__main__':
    agent = BudgetAgent('Rome.csv')
    agent.load_data()
    agent.validate_data()
    summary = agent.get_summary()
    
    if "errors" in summary:
        for error in summary['errors']:
            print(error)
    else:
        for day, data in summary.items():
            print(f"Day {day} ({data['date']}):")
            for activity in data['activities']:
                print(f"  - {activity}")
            print(f"  Total Cost: ${data['total_cost']:.2f}")
            print("-" * 20)
