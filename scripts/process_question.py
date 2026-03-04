import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types

# Setup
question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response():
    # Use Gemma 3 27B as the primary (14k daily limit)
    # Gemini 2.5 Flash Lite as a secondary backup
    model_pool = ["gemma-3-27b-it", "gemini-2.5-flash-lite"]
    
    prompt = f"""
    Return ONLY a JSON object for: "{question_input}"
    
    JSON Schema:
    1. clean_question: Professional rephrase (fix typos).
    2. category: [Science, Tech, History, Culture, Nature, General].
    3. answer: A high-quality 3-paragraph explanation.
    
    {{
      "clean_question": "...",
      "category": "...",
      "answer": "..."
    }}
    """

    for model_id in model_pool:
        try:
            print(f"Trying {model_id}...")
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Model {model_id} failed or hit limit: {e}")
            continue

    return {"clean_question": question_input, "category": "Error", "answer": "All models currently busy."}

# Process & Save with Date Folders
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
os.makedirs(os.path.dirname(date_path), exist_ok=True)

day_data = []
if os.path.exists(date_path):
    with open(date_path, "r") as f:
        try: day_data = json.load(f)
        except: pass

day_data.append(result)
with open(date_path, "w") as f:
    json.dump(day_data, f, indent=2)

print(f"Successfully saved to {date_path}")
