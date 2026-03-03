import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types

# 1. Capture the question
question = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
current_date = datetime.now().strftime("%Y-%m-%d")

def get_ai_response():
    # Attempt 1: Gemini 3 Flash + Search (The Dream)
    try:
        print("Attempting Gemini 3 Flash with Search...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=f"Today is {current_date}. Answer in 2-sentence summary + deep dive: {question}",
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
        )
        return response.text
    except Exception as e:
        print(f"Gemini 3 Search failed: {e}")
        time.sleep(2) # Brief pause to reset

    # Attempt 2: Gemini 3 Flash (Standard)
    try:
        print("Attempting Gemini 3 Flash without Search...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=question
        )
        return response.text
    except Exception as e:
        print(f"Gemini 3 Standard failed: {e}")
        time.sleep(2)

    # Attempt 3: Gemini 1.5 Flash (The Workhorse)
    # 1.5 has much higher 'free tier' availability when 3.0 is busy
    try:
        print("Falling back to Gemini 1.5 Flash...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=question
        )
        return response.text
    except Exception as e:
        return f"AI is currently over capacity. Error: {str(e)}"

# Get the best possible answer
answer_text = get_ai_response()

# --- Saving Logic remains the same ---
now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
os.makedirs(os.path.dirname(date_path), exist_ok=True)

new_entry = {"timestamp": now.isoformat(), "question": question, "answer": answer_text}
day_data = []
if os.path.exists(date_path):
    with open(date_path, "r") as f:
        try: day_data = json.load(f)
        except: pass

day_data.append(new_entry)
with open(date_path, "w") as f:
    json.dump(day_data, f, indent=2)
