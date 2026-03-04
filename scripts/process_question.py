import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types

question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response():
    # Use gemini-2.0-flash for speed or gemini-2.5-flash-lite for max quota
    model_id = "gemini-2.0-flash" 
    
    prompt = f"""
    You are a professional research logger. Analyze: "{question_input}"
    1. Clean the question: Fix typos and rephrase professionally.
    2. Categorize: Pick one (Science, Technology, History, Geography & Places, Government & Politics, Current Events & News, Culture & Entertainment, Math & Calculations, Data & Statistics, or General Knowledge).
    3. Answer: Provide a detailed 3-paragraph response from your internal knowledge.
    
    Output ONLY valid JSON:
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
            "answer": "The AI is currently catching its breath. Please try again in 60 seconds."
        }

# Process and Save
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

# Save logic
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
