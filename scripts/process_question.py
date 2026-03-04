import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types

# 1. Setup
question_input = sys.argv[1] if len(sys.argv) > 1 else "Daily check-in"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
current_date = datetime.now().strftime("%Y-%m-%d")

def get_structured_response():
    # We use a f-string with triple quotes. 
    # MAKE SURE there are three quotes at the start and three at the end.
    prompt_text = f"""
    Analyze this user question: "{question_input}"
    
    TASK:
    1. Clean up typos and rephrase it professionally.
    2. Categorize it as: General Knowledge, Geography & Places, Government & Politics, Current Events & News, Science, Technology, History, Culture & Entertainment, Math & Calculations, or Data & Statistics.
    3. Provide an accurate 3-paragraph answer.
    
    OUTPUT: Return ONLY a valid JSON object with these exact keys:
    "clean_question", "category", "answer"
    """

    try:
        # Using Gemini 2.0 Flash for best stability/speed balance
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {e}")
        return {
            "clean_question": question_input,
            "category": "General Knowledge",
            "answer": "The AI is currently at capacity or the request failed. Please try again shortly."
        }

# 2. Execute and Add Meta-Data
result = get_structured_response()
result["timestamp"] = datetime.now().isoformat()

# 3. Save to the correct Date Folder
now = datetime.now()
date_path = f"data/{now.year}/{now.month:02d}/{now.day:02d}.json"
os.makedirs(os.path.dirname(date_path), exist_ok=True)

day_data = []
if os.path.exists(date_path):
    with open(date_path, "r") as f:
        try:
            day_data = json.load(f)
        except:
            pass

day_data.append(result)

with open(date_path, "w") as f:
    json.dump(day_data, f, indent=2)

print(f"Successfully processed: {result['clean_question']}")
