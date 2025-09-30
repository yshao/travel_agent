# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Agent Travel - AI Travel Planning Assistant

## Project Overview

The **Agent Travel** project is a sophisticated multi-agent AI travel planning system built with Python and Streamlit. It provides users with personalized travel itineraries through conversational interaction, leveraging Google Gemini AI for intelligent content generation and multiple specialized agents for different aspects of travel planning.

## Quick Start Commands

```bash
# Setup and Installation
make install    # Create virtual environment with uv and install dependencies

# Running the Application
make run        # Launch Streamlit application (runs: uv run streamlit run streamlit_app.py)

# Testing
make test       # Run validation tests (evaluate_csv.py + test_generate_csv_itinerary.py)

# Individual Test Files
uv run python test_budget_agent.py           # Test budget validation
uv run python evaluate_csv.py                # Validate CSV exports
uv run python test_generate_csv_itinerary.py # Test itinerary generation

# Cleanup
make clean      # Remove virtual environment
```

## Environment Configuration

Required environment variable in `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

The Gemini API key is loaded via `python-dotenv` and used in `orchestrator.py` for LLM calls.

## Architecture & Technology Stack

### Core Technologies
- **Python 3.12** - Main programming language
- **Streamlit** - Web interface framework for interactive UI and session management
- **Google Gemini 1.5 Flash** - Large Language Model for content generation and parameter extraction
- **Pydantic v1** - Data validation and parsing with type safety (BaseModel, Field, validator)
- **Pandas** - Data manipulation for CSV processing and itinerary analysis
- **ReportLab** - PDF generation library for itinerary document exports
- **uv** - Modern Python package manager and virtual environment tool
- **python-dotenv** - Environment variable management for API keys

### Architecture Pattern

The system follows a **Multi-Agent Orchestration** architecture with three distinct layers:

#### 1. Presentation Layer
- **streamlit_app.py** - Main UI entry point with chat interface
- **Session State Management** - Persistent state via `st.session_state`
- **Download Controls** - PDF/CSV export with validation feedback

#### 2. Orchestration Layer
- **orchestrator.py** - Central coordinator managing all agent interactions
- **Phase Management** - INITIAL → ITINERARY → BUDGET phase transitions
- **State Persistence** - JSON-based trip storage in `user_trips.json`
- **LLM Integration** - Gemini API calls with structured prompt engineering

#### 3. Agent Layer (Specialized Services)
- **TravelPlannerAgent** - NLP parameter extraction from user queries
- **AirbnbAgent** - Accommodation recommendation templates
- **BudgetAgent** - Financial validation and cost analysis
- **Location RAG Tool** - Geographic verification with mock geocoding

### Design Patterns

**Orchestrator Pattern**: Central `Orchestrator` class coordinates all agent activities
```python
orchestrator = Orchestrator()
orchestrator.process_user_input(user_input, state)  # Routes to appropriate agent
```

**Phase-Based State Machine**: Three distinct phases with different behaviors
```python
state["current_phase"] = "INITIAL|ITINERARY|BUDGET"
```

**Pydantic Validation**: Type-safe data models throughout
```python
class ItineraryEntry(BaseModel):
    day: str
    date: str
    activity: str
    cost: Optional[float]
```

**Caching Strategy**: Streamlit decorators for performance
```python
@st.cache_resource  # Singleton orchestrator
@st.cache_data      # Cached trip data reads
```

## System Components & Modules

### Module Overview

```
agent_travel/
├── streamlit_app.py          # UI entry point with chat interface
├── orchestrator.py            # Central coordinator and state management
├── gemini_utils.py            # Gemini API wrapper utility
│
├── Agents/
│   ├── travel_planner_agent.py  # Parameter extraction from NLP
│   ├── budget_agent.py          # Financial validation and analysis
│   ├── airbnb_agent.py          # Accommodation recommendations
│   ├── location_rag_agent.py    # Geographic verification (deprecated)
│   └── location_rag_tool.py     # Location verification with mock data
│
├── CSV Generation/
│   ├── generate_csv_itinerary.py        # Original CSV generation
│   ├── generate_csv_itinerary_final.py  # Refined with error handling
│   └── generate_csv_itinerary_fixed.py  # Latest with full validation ⭐
│
├── Data Models/
│   └── Trip.py                  # Pydantic model for trip records
│
├── Testing/
│   ├── evaluate_csv.py                  # CSV validation testing
│   ├── test_budget_agent.py             # Budget agent unit tests
│   └── test_generate_csv_itinerary.py   # CSV generation tests
│
├── Configuration/
│   ├── .env                     # Environment variables (API keys)
│   ├── requirements.txt         # Python dependencies
│   └── Makefile                 # Build and run commands
│
└── Data/
    ├── user_trips.json          # Persistent trip storage
    ├── state_output.json        # Debug state output
    └── test_user_trips.json     # Test data
```

### 1. Core Orchestrator (`orchestrator.py`)
**Purpose**: Central coordinator managing all agent interactions and system workflow

**Key Responsibilities**:
- **Phase Management**: Routes requests through INITIAL → ITINERARY → BUDGET phases
- **State Management**: Maintains conversation state and trip data
- **Agent Coordination**: Initializes and delegates to specialized agents
- **LLM Integration**: Manages all Gemini API calls via `call_gemini()`
- **Export Generation**: PDF (ReportLab) and CSV (Pandas) creation
- **Trip Persistence**: JSON-based save/load with auto-titling

**Key Methods**:
```python
get_default_state()                    # Initialize empty state
process_user_input(input, state)       # Main request router
generate_trip_title_with_llm(plan)     # Auto-generate trip names
save_current_trip(title, state)        # Persist to JSON
load_saved_trip(title, state)          # Restore from JSON
generate_pdf_itinerary(state)          # Create PDF export
generate_csv_itinerary(state)          # Create CSV export
validate_csv_itinerary(csv_data)       # Validate with BudgetAgent
```

**Key Classes**:
- `ItineraryEntry(BaseModel)`: Pydantic model for structured itinerary data
  - Fields: day, date, activity, description, location, cost, travel_distance_to_next_location
- `Orchestrator`: Main coordination class with agent composition

### 2. Travel Planner Agent (`travel_planner_agent.py`)
**Purpose**: Natural language processing for travel parameter extraction

**Key Responsibilities**:
- **Parameter Extraction**: Parses user input for destination, duration, budget, interests
- **LLM-Based Parsing**: Uses Gemini to extract structured JSON from free-form text
- **Plan Validation**: Identifies missing parameters and returns list of gaps
- **State Updates**: Merges extracted parameters into existing plan state

**Key Methods**:
```python
parse_with_llm(user_input, current_plan)  # Extract params via Gemini, update plan
check_missing_info(plan)                   # Return list of missing required fields
```

**Extraction Pattern**:
1. Send user input to Gemini with JSON schema prompt
2. Parse response for JSON block (regex: `r"```json\n([\s\S]*?)\n```"`)
3. Merge extracted fields into current plan (non-null values only)
4. Check for missing required fields

**Required Parameters**:
- destination, duration, month, traveler_type, interests, budget

**Data Model**:
```python
plan = {
    "destination": str,           # e.g., "Rome"
    "duration": int,              # e.g., 7
    "month": str,                 # e.g., "May"
    "traveler_type": str,         # e.g., "couple"
    "interests": List[str],       # e.g., ["history", "food"]
    "budget": float,              # e.g., 3000.0
    "initial_query": str          # Original user input
}
```

### 3. Budget Agent (`budget_agent.py`)
**Purpose**: Financial analysis and cost validation for travel planning

**Key Responsibilities**:
- **CSV Loading**: Reads CSV itinerary files using Pandas
- **Data Validation**: Pydantic-based type validation for all trip records
- **Cost Parsing**: Handles various cost formats ($, commas, per person)
- **Date Validation**: Validates chronological order and format consistency
- **Summary Generation**: Groups activities by day with cost totals

**Key Methods**:
```python
load_data()       # Load CSV, handle missing Day/Date, parse costs
validate_data()   # Check day/date sequences, detect format errors
get_summary()     # Return dict of {day: {date, activities, total_cost}}
```

**Data Model**:
```python
class Trip(BaseModel):
    day: Optional[int]                              # Field(alias='Day')
    date: Optional[str]                             # Field(alias='Date')
    activity: Optional[str]                         # Field(alias='Activity')
    description: Optional[str]                      # Field(alias='Description')
    location: Optional[str]                         # Field(alias='Location')
    cost: Optional[str]                             # Auto-converted to float via validator
    travel_distance_to_next_location: Optional[float]  # Field(alias='Travel Distance...')

    @validator('cost')
    def validate_cost(cls, v):
        # Removes $, commas; converts to float
```

**Validation Logic**:
- Handles missing Day/Date by programmatically adding them (4 activities/day)
- Forward fills Day and Date for multi-activity entries
- Validates ascending day order and chronological date sequence
- Supports multiple date formats: %Y-%m-%d, %m/%d/%Y, %d/%m/%Y

### 4. Airbnb Agent (`airbnb_agent.py`)
**Purpose**: Accommodation recommendations and booking guidance

**Key Responsibilities**:
- **Template-Based Recommendations**: Provides structured neighborhood suggestions
- **Preference Matching**: Considers destination, budget, traveler_type, interests
- **Booking Disclaimer**: Clarifies no actual booking functionality

**Key Methods**:
```python
find_optimal_airbnb(plan)  # Returns formatted recommendation text
```

**Current Implementation**:
- Returns template response with placeholder neighborhoods
- Ready for API integration (Airbnb, Booking.com, etc.)
- Suggests multiple areas with example properties and pricing

### 5. Location RAG Tool (`location_rag_tool.py`)
**Purpose**: Geographic verification and location intelligence with mock geocoding

**Key Responsibilities**:
- **Mock Geocoding**: Simulates API calls with hardcoded Rome location data
- **Distance Calculations**: Haversine formula for travel distance computation
- **Coordinate Enrichment**: Returns lat/long, country, region, confidence scores
- **CSV Processing**: Adds verified location data to itinerary CSVs

**Key Classes & Methods**:
```python
class VerifiedLocation(BaseModel):
    original_input: str                    # User's location string
    verified_name: str                     # Standardized name
    coordinates: Tuple[float, float]       # (lat, lng)
    country: str                           # e.g., "Italy"
    region: str                            # e.g., "Lazio"
    confidence_score: float                # 0.0-1.0 reliability
    api_source: str                        # e.g., "Simulated Google Places"
    verification_timestamp: datetime

class LocationRAG:
    _call_geocoding_api(location_string)   # Mock geocoding with hardcoded data
    _haversine_distance(lat1, lon1, lat2, lon2)  # Calculate distance in miles
    verify_location(location_string)       # Main entry point
    process_itinerary(csv_path)            # Add location data to CSV
```

**Hardcoded Locations** (Rome-specific):
- Colosseum, Vatican City, Pantheon, Trevi Fountain, Trastevere
- Palatine Hill, Ostia Antica, Campo de' Fiori Market
- Restaurants: Trattoria Monti, Da Enzo al 29, Armando al Pantheon
- Other: Fiumicino Airport, Borghese Gallery, Appian Way

**Production Migration**:
To use real geocoding, replace `_call_geocoding_api()` with actual API:
- Google Places API
- OpenStreetMap Nominatim
- Mapbox Geocoding API

### 6. CSV Generation System (`generate_csv_itinerary*.py`)
**Purpose**: Structured itinerary export with validation

**Three Implementations**:

**6a. `generate_csv_itinerary.py`** - Original implementation
- Basic parsing of markdown itinerary from conversation history
- Extracts activities, locations, costs from formatted text
- Limited error handling

**6b. `generate_csv_itinerary_final.py`** - Refined version
- Improved parsing with better regex patterns
- Enhanced error handling for malformed entries
- Still uses basic validation

**6c. `generate_csv_itinerary_fixed.py`** ⭐ **PREFERRED**
- Full Pydantic validation with `ItineraryEntry` model
- Robust cost parsing (handles $, commas, "per person")
- Travel distance extraction and normalization
- Custom validators for data integrity

**Key Function**:
```python
def generate_csv_itinerary(state: dict) -> str:
    # 1. Extract itinerary from conversation_history
    # 2. Parse markdown format (Day X: Date: ...)
    # 3. Extract activities with @ location $ cost (travel distance)
    # 4. Validate with Pydantic ItineraryEntry
    # 5. Return CSV string
```

**Expected Markdown Format**:
```
**Day 1: July 17, 2025:**
* Colosseum (Ancient Roman amphitheater) @ Colosseum, Rome $20 (15 min walk)
* Roman Forum (Ancient marketplace) @ Roman Forum, Rome $15 (10 min walk)
```

### 7. Streamlit Interface (`streamlit_app.py`)
**Purpose**: User interface and session management

**Key Components**:

**Session State Management**:
```python
@st.cache_resource
def get_orchestrator():
    return Orchestrator()  # Singleton pattern

if 'state' not in st.session_state:
    st.session_state.state = orchestrator.get_default_state()
```

**UI Features**:
- **Chat Interface**: `st.chat_message()` with role-based display
- **Chat Input**: `st.chat_input()` with example placeholder
- **Sidebar Controls**: Save/load trips with search filtering
- **Download Buttons**: PDF and CSV exports with validation
- **State Debugging**: Expandable JSON viewer (`st.sidebar.expander()`)

**Interaction Flow**:
1. User enters query in chat input
2. `orchestrator.process_user_input(prompt, state)` processes request
3. State updated with new conversation entries
4. `st.rerun()` refreshes UI with new messages
5. Export buttons always available for download

**Save/Load System**:
- Manual save with custom title input
- Auto-save with LLM-generated titles
- Search filtering for saved trips
- Selectbox for trip selection
- Load replaces entire session state

## Workflow & Procedures

### Complete User Journey

#### 1. Application Startup
```
User runs: make run
↓
Streamlit loads streamlit_app.py
↓
@st.cache_resource initializes Orchestrator singleton
↓
Orchestrator.__init__():
  - Loads .env with GEMINI_API_KEY
  - Configures genai.configure(api_key=...)
  - Initializes TravelPlannerAgent, AirbnbAgent
↓
Session state initialized with get_default_state()
↓
Chat interface displays welcome message
```

#### 2. Phase 1: INITIAL - Parameter Extraction
```
User Input: "Plan a 7-day trip to Rome in May for a couple interested in history and food, budget $3000"
↓
streamlit_app.py: st.chat_input() captures input
↓
orchestrator.process_user_input(user_input, state)
↓
state["conversation_history"].append({"role": "user", "content": user_input})
↓
Check: state["current_phase"] == "INITIAL"
↓
travel_planner_agent.parse_with_llm(user_input, state["plan"])
  ├─ Gemini prompt: "Extract travel parameters as JSON..."
  ├─ Regex parse: r"```json\n([\s\S]*?)\n```"
  └─ Merge extracted params into state["plan"]
↓
missing_info = travel_planner_agent.check_missing_info(state["plan"])
↓
IF missing_info is empty:
  ├─ state["current_phase"] = "ITINERARY"
  ├─ Display confirmed parameters
  └─ Generate itinerary (next phase)
ELSE:
  └─ Request missing information from user
```

#### 3. Phase 2: ITINERARY - Content Generation
```
Phase transition to ITINERARY
↓
Gemini prompt construction:
  "Generate a {duration}-day itinerary for {destination} in {month}
   for {traveler_type} interested in {interests}. Budget: ${budget}
   Format: **Day X: Date:** * Activity @ Location $Cost (travel distance)"
↓
ai_response = call_gemini(prompt)
↓
state["conversation_history"].append({"role": "assistant", "content": ai_response})
↓
User presented with available commands:
  - 'details [Day X]' or 'details [attraction]'
  - 'budget estimate'
  - 'find airbnb'
  - 'generate csv'
```

**ITINERARY Phase Command Processing**:

**A. Detail Request** (`details Colosseum`):
```
User: "details Colosseum"
↓
Check: user_input.lower().startswith("details")
↓
detail_query = "Colosseum"
↓
Gemini prompt: "Provide practical details for 'Colosseum' from {destination} itinerary.
                Include time, description, address, cost, nearby attractions, booking links"
↓
Display detailed response
```

**B. Budget Estimate** (`budget estimate`):
```
User: "budget estimate"
↓
Check: user_input.lower() == "budget estimate"
↓
state["current_phase"] = "BUDGET"
↓
Gemini prompt: "Provide budget breakdown for {duration}-day trip to {destination}
                with ${budget}. Categories: flights, accommodation, food, activities"
↓
Display cost breakdown and optimization tips
```

**C. Airbnb Search** (`find airbnb`):
```
User: "find airbnb"
↓
Check: user_input.lower() == "find airbnb"
↓
airbnb_agent.find_optimal_airbnb(state["plan"])
↓
Template response with neighborhood suggestions
```

#### 4. Phase 3: BUDGET - Financial Analysis
```
state["current_phase"] == "BUDGET"
↓
Budget breakdown already generated
↓
User options:
  - Continue conversation: General responses
  - 'new plan': Reset to INITIAL phase with get_default_state()
```

#### 5. Export Operations (Available in All Phases)

**PDF Export**:
```
User clicks: "Download Itinerary as PDF"
↓
streamlit_app.py: orchestrator.generate_pdf_itinerary(json.dumps(state))
↓
orchestrator.generate_pdf_itinerary():
  ├─ Search conversation_history for itinerary (heuristic: "Day 1:" present)
  ├─ Create ReportLab document with SimpleDocTemplate
  ├─ Add paragraphs for each line
  └─ Return BytesIO buffer
↓
st.download_button delivers PDF file
```

**CSV Export with Validation**:
```
User clicks: "Validate and Download CSV"
↓
orchestrator.generate_csv_itinerary(json.dumps(state))
  ├─ Call generate_csv_itinerary(state) from module
  ├─ Parse itinerary markdown from conversation_history
  ├─ Regex extraction: Day, Date, Activity, Location, Cost, Travel Distance
  ├─ Pydantic validation with ItineraryEntry model
  └─ Return CSV string
↓
orchestrator.validate_csv_itinerary(csv_data)
  ├─ Write CSV to temp file
  ├─ process_itinerary(temp_file) # Location RAG adds verification
  ├─ BudgetAgent(temp_file).load_data()
  ├─ BudgetAgent.validate_data() # Check sequences and formats
  └─ Return summary or errors
↓
IF validation_results["errors"]:
  └─ Display error messages
ELSE:
  ├─ Show success message
  └─ st.download_button delivers CSV file
```

#### 6. Save/Load Operations

**Save Trip**:
```
User enters trip title: "Rome Vacation 2025"
User clicks: "Save Current Trip"
↓
orchestrator.save_current_trip(title, state)
↓
IF title is empty:
  ├─ generate_trip_title_with_llm(plan, initial_query)
  ├─ Gemini generates concise title
  └─ Use generated title
↓
save_trip_data(title, state)
  ├─ Read all_trips from user_trips.json
  ├─ all_trips[title] = state
  ├─ Write back to user_trips.json
  └─ Invalidate Streamlit cache
↓
Success message added to conversation_history
```

**Load Trip**:
```
User searches: "Rome"
↓
Sidebar filters trip titles containing "Rome"
↓
User selects: "Rome Vacation 2025"
User clicks: "Load Selected Trip"
↓
orchestrator.load_saved_trip(title, state)
↓
loaded_state = load_trip_data(title)
  ├─ Read all_trips from user_trips.json
  └─ Return all_trips.get(title)
↓
IF loaded_state exists:
  ├─ st.session_state.state = loaded_state
  └─ st.rerun() to refresh UI
ELSE:
  └─ Error message: "No trip found"
```

### State Management Architecture

#### Session State Structure
```python
state = {
    "current_phase": "INITIAL|ITINERARY|BUDGET",
    "plan": {
        "destination": str,              # e.g., "Rome"
        "duration": int,                 # e.g., 7
        "month": str,                    # e.g., "May"
        "traveler_type": str,            # e.g., "couple"
        "interests": List[str],          # e.g., ["history", "food"]
        "budget": float,                 # e.g., 3000.0
        "initial_query": str             # Original user input
    },
    "conversation_history": [
        {"role": "user", "content": "Plan a trip to Rome..."},
        {"role": "assistant", "content": "I'll help you plan..."}
    ]
}
```

**State Transitions**:
```
INITIAL → ITINERARY: When all required parameters extracted
ITINERARY → BUDGET: When user requests "budget estimate"
BUDGET → INITIAL: When user requests "new plan" (state reset)
```

#### Persistence Layer
- **File Storage**: `user_trips.json` with structure `{trip_title: state_dict}`
- **Caching Strategy**:
  - `@st.cache_resource` for Orchestrator singleton (never invalidated)
  - `@st.cache_data` for trip reads (invalidated on writes)
- **Auto-Titling**: LLM-generated titles via `generate_trip_title_with_llm()`
- **Search Functionality**: Client-side filtering with `title.lower() in search.lower()`

### Key Technical Details

#### LLM Prompt Engineering Patterns

**Parameter Extraction Prompt**:
```python
prompt = f"""
Extract the following travel planning parameters from the user's input.
Return the information as a JSON object with the keys:
'destination', 'duration', 'month', 'traveler_type', 'interests', 'budget'.
If a value is not present, set it to null.

User Input: '{user_input}'
"""
```

**Itinerary Generation Prompt** (in orchestrator.py:226-236):
```python
prompt = f"""Generate a {duration}-day itinerary for a trip to {destination} in {month}
for {traveler_type} interested in {interests}. Budget: ${budget}.
For each day, include specific date (e.g., July 17, 2025).
Format as described in PROMPT.md:

**Day 1: [Date]: ...**
* Activity Name (Description) @ Location $Cost (Travel Distance to Next Location)
...
"""
```

#### Regex Patterns for Parsing

**JSON Extraction from Markdown**:
```python
json_match = re.search(r"```json\n([\s\S]*?)\n```", response_text)
```

**Day Header Parsing** (in generate_csv_itinerary_fixed.py:66):
```python
day_pattern = re.compile(r"^(?:##|\*\*)\s*Day (\d+):\s*([A-Za-z]+\s+\d{1,2},\s+\d{4}):(.*)$")
# Matches: **Day 1: July 17, 2025:** or ## Day 1: July 17, 2025:
```

**Activity Line Parsing**:
```python
activity_line_start_pattern = re.compile(r"^\*\s*(.*)$")
# Matches: * Activity text here
```

**Cost Extraction** (in generate_csv_itinerary_fixed.py:95-98):
```python
cost_chunk_with_paren_pattern = re.compile(r"(\s*\(\s*\$([\d,.]+)(?:\s*per person)?\s*\))")
# Matches: ($25), ($25 per person), ($ 25), etc.
```

#### Error Handling Patterns

**Graceful LLM Failures**:
```python
try:
    response = model.generate_content(prompt)
    return response.text
except Exception as e:
    return f"Error calling Gemini API: {e}"
```

**Pydantic Validation Errors**:
```python
try:
    entry = ItineraryEntry(**row.to_dict())
    self.trips.append(entry)
except ValueError as e:
    self.errors.append(f"Row {index + 2}: {e}")
```

**File Not Found Handling**:
```python
if not os.path.exists(TRIP_DATA_FILE) or os.path.getsize(TRIP_DATA_FILE) == 0:
    return {}
```

#### Performance Optimizations

**Singleton Pattern for Orchestrator**:
```python
@st.cache_resource
def get_orchestrator():
    return Orchestrator()  # Only instantiated once
```

**Cached Trip Reads**:
```python
@st.cache_data
def _read_all_trips(_self):  # Note: _self to prevent hashing
    # Reads cached, writes invalidate
```

**Cache Invalidation on Writes**:
```python
def _write_all_trips(_self, all_trips):
    _self._read_all_trips.clear()      # Invalidate read cache
    _self.get_all_trip_titles.clear()   # Invalidate titles cache
```

### Testing Strategy

#### Unit Tests
- **`test_budget_agent.py`**: Tests BudgetAgent CSV loading and validation
- **`test_generate_csv_itinerary.py`**: Tests CSV generation from state

#### Integration Tests
- **`evaluate_csv.py`**: End-to-end CSV validation with BudgetAgent

#### Test Data
- **`test_user_trips.json`**: Sample saved trips for testing
- **`test_invalid_itinerary.json`**: Error cases for validation testing
- **`Rome.csv`**: Sample CSV itinerary for budget agent testing

#### Running Tests
```bash
make test                           # Run all tests
uv run python test_budget_agent.py  # Test budget validation
uv run python evaluate_csv.py       # Test CSV validation
```

### Critical Implementation Details

#### State Management Flow
The orchestrator maintains three distinct phases:
1. **INITIAL**: Parameter extraction via `TravelPlannerAgent.parse_with_llm()`
2. **ITINERARY**: Content generation via `call_gemini()` with structured prompts
3. **BUDGET**: Cost analysis and breakdown generation

State persists in `st.session_state.state` and is saved to `user_trips.json` for cross-session persistence.

#### Gemini API Integration Pattern
All LLM calls go through `call_gemini()` in `orchestrator.py`:
```python
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)
```

Rate limiting is simulated in `location_rag_tool.py` with 0.1s delays. For production, implement proper throttling.

#### CSV Generation Versions
Three implementations exist with different approaches:
- `generate_csv_itinerary.py` - Original implementation
- `generate_csv_itinerary_final.py` - Refined version with better error handling
- `generate_csv_itinerary_fixed.py` - Latest with complete validation

Use the `_fixed` version for new features as it has the most robust Pydantic validation.

#### Location Verification System
`location_rag_tool.py` currently uses **mock data** for Rome locations. To integrate real geocoding:
1. Replace `_call_geocoding_api()` method with actual API calls
2. Add API key configuration for Google Places/OpenStreetMap
3. Update confidence scoring logic based on API response quality

## Data Flow Architecture

### Input Processing
```
Natural Language Input
↓ Travel Planner Agent
Structured Parameters
↓ Orchestrator Validation
Confirmed Plan
↓ Gemini API
Generated Itinerary
```

### Location Processing
```
Location Strings
↓ Location RAG Tool
Geographic Verification
↓ Coordinate Validation
Verified Locations with Confidence Scores
```

### Export Processing
```
Conversation State
↓ Format Selection (PDF/CSV)
Data Validation
↓ Pydantic Models
Structured Export
↓ File Generation
Download Delivery
```

## Key Features & Capabilities

### Conversational Intelligence
- **Natural Language Processing**: Extracts travel parameters from free-form text
- **Context Awareness**: Maintains conversation history and state
- **Clarification Handling**: Requests missing information intelligently
- **Multi-Turn Dialogue**: Supports iterative refinement of plans

### Multi-Format Export
- **PDF Generation**: Professional itinerary documents via ReportLab
- **CSV Export**: Structured data with validation and verification
- **Data Integrity**: Pydantic model validation for all exports
- **Validation Feedback**: Error reporting for invalid data

### Geographic Intelligence
- **Location Verification**: Coordinate-based validation of destinations
- **Distance Calculation**: Travel logistics with Haversine formula
- **Confidence Scoring**: Reliability metrics for location data
- **API Integration Ready**: Extensible for real geocoding services

### Budget Optimization
- **Cost Breakdown**: Detailed analysis by category
- **Optimization Tips**: Actionable suggestions for budget management
- **Financial Validation**: Type-safe cost processing
- **Planning Tools**: Budget estimation and tracking

## Development Guidelines

### Adding New Agents
When creating new specialized agents (e.g., Restaurant Agent, Transport Agent):
1. Follow the pattern in `travel_planner_agent.py`, `budget_agent.py`, `airbnb_agent.py`
2. Import and initialize in `orchestrator.py`
3. Add agent method calls within appropriate phase logic
4. Update state structure if new data fields are needed

### Modifying Itinerary Generation
Itinerary prompts are in `orchestrator.py` within phase-specific logic. When updating:
1. Modify the prompt string passed to `call_gemini()`
2. Test with multiple destinations to ensure generalization
3. Update Pydantic `ItineraryEntry` model if new fields are added
4. Re-run `make test` to validate CSV generation

### Extending Export Formats
Current exports: PDF (ReportLab), CSV (Pandas/Pydantic)
To add new formats (e.g., JSON, DOCX):
1. Add generation method in `orchestrator.py` (follow `generate_pdf_itinerary` pattern)
2. Add download button in `streamlit_app.py`
3. Include validation logic similar to CSV validation
4. Create test file in root directory

### Working with Location Data
The mock geocoding system in `location_rag_tool.py` needs replacement for production:
- Current: Hardcoded Rome locations with dummy coordinates
- Production: Integrate Google Places API, OpenStreetMap Nominatim, or Mapbox Geocoding
- Distance calculations use Haversine formula (already implemented)
- Maintain `VerifiedLocation` Pydantic model structure for type safety

## Common Development Patterns

### LLM Response Parsing
Responses from Gemini often contain JSON in markdown code blocks:
```python
json_match = re.search(r"```json\n([\s\S]*?)\n```", response_text)
if json_match:
    json_str = json_match.group(1)
    data = json.loads(json_str)
```

### Pydantic Validation Pattern
All data models use Pydantic for type safety:
```python
class ModelName(BaseModel):
    field: type = Field(..., description="purpose")

    @validator('field')
    def validate_field(cls, v):
        # validation logic
        return v
```

### Streamlit State Management
State persists across reruns via `st.session_state`:
```python
if 'state' not in st.session_state:
    st.session_state.state = orchestrator.get_default_state()
state = st.session_state.state
```

After processing: `st.session_state.state = orchestrator.process_user_input(prompt, state)` then `st.rerun()`