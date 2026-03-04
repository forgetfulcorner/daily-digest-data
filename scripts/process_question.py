import os, json, sys, re
from datetime import datetime
from google import genai
from google.genai import types

# Setup
question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response():
    model_id = "gemini-2.5-flash-lite"
    categories = ["General Knowledge", "Geography & Places", "Government & Politics", "Current Events & News", "Science", "Technology", "History", "Culture & Entertainment", "Math & Calculations", "Data & Statistics"]
    
    prompt = f"Return ONLY JSON for: {question_input}. Cat: {categories}. Structure: {{'clean_question': '...', 'category': '...', 'answer': '...'}}"
    
    response = client.models.generate_content(
        model=model_id, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

# Process
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

# 1. Save to Daily Folder (Existing Logic)
now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
os.makedirs(os.path.dirname(date_path), exist_ok=True)
day_data = json.load(open(date_path)) if os.path.exists(date_path) else []
day_data.append(result)
with open(date_path, "w") as f: json.dump(day_data, f, indent=2)

# 2. Save to Master Index (New Logic for "All Posts")
master_path = "data/all_posts.json"
master_data = json.load(open(master_path)) if os.path.exists(master_path) else []
master_data.append(result)
with open(master_path, "w") as f: json.dump(master_data, f, indent=2)

print(f"Logged to daily and master index.")
