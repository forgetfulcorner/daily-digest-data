import os, json, sys
from datetime import datetime
from google import genai
from google.genai import types

# 1. Capture the question from the iPhone/Action
try:
    # Use a default if run manually without arguments
    question = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "What is the weather like today?"
except Exception:
    question = "Daily check-in"

# 2. Initialize Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

print(f"Attempting to process with Gemini 3 Flash: {question}")

try:
    # 3. Use the 2026 Standard: Gemini 3 Flash
    # We include the date so Google Search Grounding knows exactly what 'today' means
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=f"Today is {current_date}. Provide a 2-sentence summary, a deep dive paragraph, and sources for: {question}",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    answer_text = response.text
except Exception as e:
    print(f"Primary request failed: {e}")
    # Fallback: Try without Google Search grounding if it's a quota/tool issue
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=question
    )
    answer_text = response.text

# 4. Save Logic
now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
os.makedirs(os.path.dirname(date_path), exist_ok=True)

new_entry = {
    "timestamp": now.isoformat(),
    "question": question,
    "answer": answer_text
}

# Append to today's list
day_data = []
if os.path.exists(date_path):
    with open(date_path, "r") as f:
        try:
            day_data = json.load(f)
        except: day_data = []

day_data.append(new_entry)

with open(date_path, "w") as f:
    json.dump(day_data, f, indent=2)

print(f"Successfully saved to {date_path}")
