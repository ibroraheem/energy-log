import google.generativeai as genai
import os

# Use the key provided by user (hardcoded for this check script as I don't want to parse secrets again here for a quick check)
api_key = "AIzaSyDPh-57lPo2JqkjxcHIaS1RO5dFwjOWZk0" 
genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
