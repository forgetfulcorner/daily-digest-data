import os, json, sys, re, time
from datetime import datetime
from google import genai
from google.genai import types
from google.genai import errors # Import errors for specific catching

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
    
    prompt = f"""
    You are an expert educator. Process: "{question_input}"
    1. CLEAN: Rephrase as a professional, curious title.
    2. CATEGORIZE: Select EXACTLY one: {categories}.
    3. ANSWER: Provide a deep, engaging response (200-750 words). 
       - Use Markdown (bolding, bullet points, headers) for readability.
       - Ensure the tone is sophisticated yet accessible.
    
    OUTPUT ONLY VALID JSON:
    {{
      "clean_question": "string",
      "category": "string",
      "answer": "string"
    }}
    """

    # Retry Logic: Attempt 3 times if server is busy
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model_id, 
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except errors.ServerError as e:
            if "503" in str(e) and attempt < 2:
                print(f"Server busy (503). Retrying in 5 seconds... (Attempt {attempt + 1})")
                time.sleep(5)
                continue
            raise e 
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"clean_question": question_input, "category": "General Knowledge", "answer": "The AI is currently under heavy load. Please try again shortly."}

# --- Save Logic (Daily & Master) ---
result = get_ai_response()
result["timestamp"] = datetime.now().isoformat()

now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
master_path = "data/all_posts.json"

for path in [date_path, master_path]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Load existing data or create empty list
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    data.append(result)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

print(f"Successfully logged to {date_path} and master archive.")
