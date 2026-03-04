import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types

# Setup
question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response():
    # Gemma 3 27B has a 14,400/day limit on the 2026 Free Tier
    model_id = "gemma-3-27b" 
    
    prompt = f"""
    Return a JSON object for this question: "{question_input}"
    
    1. clean_question: Rephrase professionally (fix typos).
    2. category: One of [Science, Tech, History, Culture, Nature, General].
    3. answer: A high-quality 3-paragraph explanation.
    
    Output ONLY JSON:
    {{
      "clean_question": "...",
      "category": "...",
      "answer": "..."
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
            "category": "General",
            "answer": "The AI is currently resetting. Please try again in a moment."
        }

# Process & Save
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

# Save logic with date folders
now = datetime.now()
# IMPORTANT: Use UTC to match GitHub Actions' server time
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

print(f"Success: {result['clean_question']}")
