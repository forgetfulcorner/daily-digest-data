import os, json, sys, time, re
from datetime import datetime
from google import genai
from google.genai import types

# Setup
question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response():
    # Using the high-efficiency model from your 2026 usage chart
    model_id = "gemini-2.5-flash-lite"
    
    # We explicitly list your categories here so the AI has a "Menu" to choose from
    categories = [
        "General Knowledge", "Geography & Places", "Government & Politics", 
        "Current Events & News", "Science", "Technology", "History", 
        "Culture & Entertainment", "Math & Calculations", "Data & Statistics"
    ]

    prompt = f"""
    You are a professional editor. Process this input: "{question_input}"
    
    1. CLEAN: Fix typos and rephrase the question as a professional title.
    2. CATEGORIZE: Select EXACTLY one from this list: {', '.join(categories)}.
    3. ANSWER: Provide a detailed 3-paragraph educational response.
    
    OUTPUT ONLY VALID JSON:
    {{
      "clean_question": "string",
      "category": "string",
      "answer": "string"
    }}
    """

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {e}")
        return {
            "clean_question": question_input,
            "category": "General Knowledge",
            "answer": "The AI is currently resetting. Your question has been logged."
        }

# Process and Save
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

# Use UTC time to stay consistent with GitHub Actions servers
now = datetime.now()
dir_path = f"data/{now.year}/{now.month:02d}"
file_path = f"{dir_path}/{now.day:02d}.json"

os.makedirs(dir_path, exist_ok=True)

day_data = []
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        try:
            day_data = json.load(f)
        except:
            day_data = []

day_data.append(result)

with open(file_path, "w") as f:
    json.dump(day_data, f, indent=2)

print(f"FILE_WRITTEN: {file_path}")
print(f"CATEGORY_ASSIGNED: {result['category']}")
