import os, json, sys, base64
from datetime import datetime
from google import genai
from google.genai import types

# 1. Get the question from the iPhone
question = sys.argv[1]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_KEY)

# 2. Ask Gemini with Google Search Grounding
print(f"Thinking about: {question}...")
response = client.models.generate_content(
    model="gemini-2.0-flash", # Flash is fastest for this
    contents=f"Provide a 2-sentence summary, a deep dive paragraph, and sources for: {question}",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)

# 3. Create the data structure
new_entry = {
    "timestamp": datetime.now().isoformat(),
    "question": question,
    "answer": response.text,
    "sources": [source.url for source in response.candidates[0].grounding_metadata.grounding_chunks if hasattr(source, 'url')]
}

# 4. Save to the daily file
date_path = datetime.now().strftime("data/%Y/%m/%d.json")
os.makedirs(os.path.dirname(date_path), exist_ok=True)

# Load existing data if file exists
data = []
if os.path.exists(date_path):
    with open(date_path, "r") as f:
        data = json.load(f)

data.append(new_entry)

with open(date_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"Saved to {date_path}")
