import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Gemini API Configuration ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print(f"Gemini API key loaded: {bool(gemini_api_key)}") # Debug print
else:
    print("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")

def call_gemini(prompt):
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
