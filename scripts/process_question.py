import os, json, sys
from datetime import datetime
from google import genai
from google.genai import types

# 1. Capture the question
try:
    question = sys.argv[1]
except IndexError:
    question = "No question provided."

# 2. Initialize Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 3. Use Gemini 1.5 Flash (Widest Free Availability)
print(f"Attempting to process: {question}")
try:
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=f"Summary (2 sentences), Deep Dive (1 paragraph), and Sources for: {question}",
        config=types.GenerateContentConfig(
            # We'll keep search on; if it fails, we'll know it's a tool restriction
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    answer_text = response.text
except Exception as e:
    print(f"Search Grounding failed or Quota hit: {e}")
    # Fallback: Try without Google Search tool if the first one fails
    response = client.models.generate_content(
        model="gemini-1.5-flash",
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
