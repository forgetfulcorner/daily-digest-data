
import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types

question = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
current_date = datetime.now().strftime("%Y-%m-%d")

def get_ai_response():
    # Attempt 1: Gemini 2.0 Flash (The current stable standard)
    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite-preview-02-05"]
    
    for model_name in models_to_try:
        try:
            print(f"Attempting {model_name}...")
            response = client.models.generate_content(
                model=model_name, 
                contents=f"Today is {current_date}. Answer in a 2-sentence summary + deep dive: {question}",
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            return response.text
        except Exception as e:
            print(f"{model_name} failed: {e}")
            time.sleep(1)

    # Final Fallback: No tools, just the brain
    try:
        return client.models.generate_content(model="gemini-2.0-flash", contents=question).text
    except:
        return "AI is currently at peak capacity. Please try again in a few minutes."

answer_text = get_ai_response()

# --- Saving Logic ---
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
