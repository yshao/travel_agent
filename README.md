---
title: AI Travel Planning Assistant
emoji: ✈️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# ✈️ AI Travel Planning Assistant

An intelligent multi-agent system for personalized travel itinerary planning powered by Google Gemini LLM.

## 🌟 Features

- **Natural Language Planning**: Describe your trip in plain English and get a complete itinerary
- **Multi-Agent Architecture**: Specialized agents for travel planning, budget analysis, and accommodations
- **Phase-Based Workflow**:
  - INITIAL: Parameter extraction from conversational input
  - ITINERARY: Content generation with daily activities
  - BUDGET: Financial analysis and cost breakdown
- **Export Capabilities**: Download itineraries as PDF or validated CSV
- **Location Intelligence**: Geographic verification with distance calculations
- **Session Management**: Save and load multiple trip plans

## 🏗️ Architecture

The system uses an Orchestrator pattern coordinating three specialized agents:
- **Travel Planner Agent**: NLP parameter extraction via Gemini
- **Budget Agent**: Financial validation with Pandas/Pydantic
- **Airbnb Agent**: Accommodation recommendation templates

## 💻 Tech Stack

- **Python 3.12** with Pydantic v1 for type-safe data validation
- **Google Gemini 1.5 Flash** for LLM operations
- **Streamlit** for interactive chat interface
- **ReportLab** for PDF generation
- **Pandas** for CSV processing

## 🚀 Usage

1. Enter your travel request in natural language:
   - Example: "Plan a 7-day trip to Rome in May for a couple interested in history and food, budget $3000"

2. The assistant will extract parameters and ask for any missing information

3. Once confirmed, it generates a detailed daily itinerary

4. Use commands like:
   - `details [Day X]` - Get more info about a specific day
   - `budget estimate` - See cost breakdown
   - `find airbnb` - Get accommodation suggestions

5. Export your itinerary as PDF or CSV

## ⚙️ Configuration

This Space requires a `GEMINI_API_KEY` environment variable to be set in the Space Settings.

## 📝 License

MIT License

## 🙏 Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) and deployed on Hugging Face Spaces.
