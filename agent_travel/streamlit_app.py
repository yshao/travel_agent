import streamlit as st
import json
import re
import os
import datetime
from orchestrator import Orchestrator

# --- State Management ---
@st.cache_resource
def get_orchestrator():
    return Orchestrator()

orchestrator = get_orchestrator()
if 'state' not in st.session_state:
    st.session_state.state = orchestrator.get_default_state()
state = st.session_state.state

# --- UI ---
st.title("AI Travel Planning Assistant")

# Show initial message only on first run
if not state["conversation_history"]:
    st.info("Welcome to the AI Travel Planning Assistant! Please describe your travel plans. For example: 'Plan a 7-day trip to Rome in May for a couple interested in history and food, with a budget of $3000.'")

# Save/Load Trip UI
st.sidebar.header("Save/Load Trip")
trip_title_save_input = st.sidebar.text_input("Save Trip As:", key="trip_title_save_input")

if st.sidebar.button("Save Current Trip", use_container_width=True):
    if trip_title_save_input:
        st.session_state.state = orchestrator.save_current_trip(trip_title_save_input, state)
        st.rerun()
    else:
        st.session_state.state = orchestrator.save_current_trip("", state) # Auto-generate title
        st.rerun()

st.sidebar.markdown("--- ")
st.sidebar.header("Load Saved Trip")
search_query = st.sidebar.text_input("Search Trip Titles:", key="search_trip_input")

saved_trip_titles = orchestrator.get_all_trip_titles()
filtered_trip_titles = [title for title in saved_trip_titles if search_query.lower() in title.lower()]

if filtered_trip_titles:
    selected_trip_to_load = st.sidebar.selectbox("Select a trip to load:", options=filtered_trip_titles, key="selected_trip_to_load")
    if st.sidebar.button("Load Selected Trip", use_container_width=True):
        st.session_state.state = orchestrator.load_saved_trip(selected_trip_to_load, state)
        st.rerun()
else:
    st.sidebar.info("No matching trips found.")

# Display current state for debugging
st.sidebar.expander("Current App State").json(state)

# Display conversation history
for entry in state["conversation_history"]:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])


if prompt := st.chat_input("Plan a 7-day trip to Rome in May for a couple interested in history and food, with a budget of $3000."):
    # Process user input using the orchestrator
    st.session_state.state = orchestrator.process_user_input(prompt, state)
    # Rerun to display the latest messages
    st.rerun()

# Download buttons
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    pdf_data = orchestrator.generate_pdf_itinerary(json.dumps(state, default=str))
    st.download_button(
        label="Download Itinerary as PDF",
        data=pdf_data,
        file_name=f"{str(state["plan"].get("destination", "travel_itinerary")).replace(" ", "_")}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
with col_dl2:
    if st.button("Validate and Download CSV", use_container_width=True):
        csv_data = orchestrator.generate_csv_itinerary(json.dumps(state))
        validation_results = orchestrator.validate_csv_itinerary(csv_data)

        if "errors" in validation_results and validation_results["errors"]:
            st.error("CSV Validation Failed!")
            for error in validation_results["errors"]:
                st.write(error)
        else:
            st.success("CSV Validation Passed!")
            st.download_button(
                label="Download Itinerary as CSV",
                data=csv_data,
                file_name=f"{str(state["plan"].get("destination", "travel_itinerary")).replace(" ", "_")}.csv",
                mime="text/csv",
                use_container_width=True
            )