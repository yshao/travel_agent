# Trip Budget Tool Development Prompt

You are tasked with building a comprehensive trip budget tracking tool that processes CSV travel data using the provided Pydantic model. The tool must handle date validation, daily cost summation, and provide clear trip analysis capabilities.

## Pydantic Model Schema

Use this exact Pydantic model for data validation and processing:

```python
from pydantic import BaseModel, Field
from typing import Optional

class Trip(BaseModel):
    """A Pydantic model to represent a trip record from a CSV file."""
    day: Optional[int] = Field(None, alias='Day')
    date: Optional[str] = Field(None, alias='Date')
    activity: Optional[str] = Field(None, alias='Activity')
    description: Optional[str] = Field(None, alias='Description')
    location: Optional[str] = Field(None, alias='Location')
    cost: Optional[str] = Field(None, alias='Cost')
    travel_distance_to_next_location: Optional[str] = Field(None, alias='Travel Distance to Next Location')
```

## Core Requirements

### 1. CSV Data Processing with Pydantic
- Read CSV files containing trip/travel data matching the Trip model schema
- Use Pydantic's validation capabilities to ensure data integrity
- Handle CSV headers that match the model aliases ('Day', 'Date', 'Activity', etc.)
- Process records through the Trip model to catch validation errors
- Convert cost strings to proper numeric values for calculations

### 2. Date and Day Sequence Validation
- **Critical Feature**: Verify that both `day` numbers and `date` fields are in ascending order (smallest to largest)
- Validate that day numbers are sequential (1, 2, 3, etc.) with no gaps or duplicates
- Ensure dates are chronologically ordered and match the corresponding day numbers
- Support common date formats in the date field: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY
- Cross-validate that day sequence aligns with date sequence

### 3. Daily Cost Summation Logic
- Group all trip records by `day` and `date`
- Parse cost strings and convert to numeric values (handle currency symbols, commas)
- Calculate accurate daily totals for each day of the trip
- Handle multiple activities per day correctly
- Separate summations by:
  - Daily activity costs
  - Daily travel costs (if applicable)
  - Total daily expenses
  - Running trip total

### 4. Trip Data Validation Using Pydantic
- Leverage Pydantic's built-in validation for type checking
- Handle Optional fields gracefully when data is missing
- Validate cost field formats and convert to decimal/float for calculations
- Ensure day numbers are valid integers when present
- Validate location and activity fields for completeness

### 5. Enhanced Trip Analysis Features
- Display daily itinerary with costs breakdown
- Track location changes and associated travel distances
- Categorize expenses by activity type
- Calculate cost per location and cost per activity
- Generate trip summary statistics (total cost, average daily spend, most expensive day)

## Technical Implementation Guidelines

### Pydantic Integration
- Use the Trip model for all CSV row parsing
- Implement proper error handling for Pydantic validation errors
- Create batch processing for multiple Trip records
- Handle validation errors gracefully and report specific field issues

### Data Processing Pipeline
```python
# Example processing flow
1. Read CSV file
2. Parse each row through Trip model
3. Validate day/date sequence
4. Convert cost strings to numbers
5. Group by day for summation
6. Generate reports and analysis
```

### Error Handling
- Capture and report Pydantic validation errors with row numbers
- Provide specific feedback on malformed cost data
- Handle missing required fields (day, date, cost)
- Report sequence validation failures with exact problematic records

## Expected Output Format

The tool should produce:

### 1. Trip Validation Report
```
✓ Trip data validation: X records processed, Y validation errors
✓ Day sequence check: PASSED/FAILED (Days 1-N in order)
✓ Date sequence check: PASSED/FAILED (Chronological order confirmed)
✓ Cost data validation: PASSED/FAILED (All costs parseable)
✓ Trip duration: N days from [start_date] to [end_date]
```

### 2. Daily Trip Summary
```
Day | Date       | Location        | Activities | Daily Cost | Running Total
1   | 2024-07-01 | New York       | 2          | $245.50    | $245.50
2   | 2024-07-02 | Philadelphia   | 3          | $180.75    | $426.25
3   | 2024-07-03 | Washington DC  | 2          | $195.00    | $621.25
```

### 3. Activity Breakdown per Day
```
Day 1 - New York ($245.50):
  • Hotel check-in: $120.00
  • Dinner at restaurant: $85.50
  • Museum visit: $40.00

Day 2 - Philadelphia ($180.75):
  • Breakfast: $25.00
  • Liberty Bell tour: $15.00
  • Lunch: $35.75
  • Hotel: $105.00
```

### 4. Validation Error Log
```
Row 5: ValidationError - 'cost' field "invalid_amount" cannot be converted to number
Row 12: Sequence Error - Day 8 appears before Day 7
Row 18: ValidationError - 'day' field must be integer, got "3a"
```

## Specific Requirements for Trip Data

### Cost Field Processing
- Parse cost strings that may contain currency symbols ($, €, £)
- Handle comma-separated numbers (e.g., "1,234.56")
- Convert to consistent numeric format for calculations
- Validate that costs are positive numbers

### Location and Travel Tracking
- Track location changes between days
- Utilize `travel_distance_to_next_location` field for travel analysis
- Calculate total trip distance if distance data is available
- Generate location-based cost summaries

### Activity Analysis
- Group costs by activity type
- Identify most expensive activities
- Track activity patterns across locations

## Acceptance Criteria

- [ ] Successfully processes CSV files through the Trip Pydantic model
- [ ] Validates both day number and date chronological sequences
- [ ] Accurately sums costs for each day with proper numeric conversion
- [ ] Handles Pydantic validation errors with clear error reporting
- [ ] Provides comprehensive trip analysis and cost breakdowns
- [ ] Maintains data accuracy with proper currency/cost parsing
- [ ] Exports processed trip data with daily summaries
- [ ] Cross-validates day numbers against date sequence

## Bonus Features (Optional)
- Trip budget vs. actual spending comparison
- Cost per mile/kilometer analysis using travel distance data
- Activity recommendation based on cost efficiency
- Multi-trip comparison capabilities
- Export to travel planning formats
- Integration with mapping services for location validation
- Currency conversion for international trips

Build this tool focusing on the Pydantic model integration, accurate sequence validation, and precise daily cost summation. The tool should be robust enough to handle real-world trip planning CSV data with proper validation and reporting.