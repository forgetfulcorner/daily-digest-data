import os, json, sys, re
from datetime import datetime
from google import genai
from google.genai import types

# Setup
question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response():
    model_id = "gemini-2.5-flash-lite"
    categories = [
        "General Knowledge", "Geography & Places", "Government & Politics", 
        "Current Events & News", "Science", "Technology", "History", 
        "Culture & Entertainment", "Math & Calculations", "Data & Statistics"
    ]
    
    # NEW: Demand depth, formatting, and word count
    prompt = f"""
    You are an expert educator. Process: "{question_input}"
    
    1. CLEAN: Rephrase as a professional, curious title.
    2. CATEGORIZE: Select EXACTLY one: {categories}.
    3. ANSWER: Provide a deep, engaging response (200-750 words). 
       - Use Markdown (bolding, bullet points) for readability.
       - Cover the biological, social, and behavioral aspects of the topic.
       - Ensure the tone is sophisticated yet accessible.
    
    OUTPUT ONLY VALID JSON:
    {{
      "clean_question": "string",
      "category": "string",
      "answer": "string (using markdown for formatting)"
    }}
    """
    
    response = client.models.generate_content(
        model=model_id, 
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

# --- Save Logic (Daily & Master) ---
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
master_path = "data/all_posts.json"

for path in [date_path, master_path]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = json.load(open(path)) if os.path.exists(path) else []
    data.append(result)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

print(f"Logged: {result['clean_question']} to {date_path} and master index.")
