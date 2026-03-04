import os, json, sys, time
from datetime import datetime
from google import genai
from google.genai import types
import re

# --- Configuration ---
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash"
DATA_DIR = "data"

# Free-tier safe: no search, no retries, simple call
client = genai.Client(api_key=API_KEY)

# --- Input ---
raw_question = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "Daily check-in"

# --- 1) Clean up question ---
def clean_question(text):
    # Remove extra whitespace, fix basic punctuation
    text = re.sub(r"\s+", " ", text.strip())
    if not text.endswith("?"):
        text += "?"
    return text

question = clean_question(raw_question)

# --- 2) Category classification prompt ---
CATEGORIES = [
    "General Knowledge", "Geography & Places", "Government & Politics",
    "Current Events & News", "Science", "Technology", "History",
    "Culture & Entertainment", "Math & Calculations", "Data & Statistics"
]

category_prompt = f"""
Classify the following question into ONE of these categories: {', '.join(CATEGORIES)}.
Question: {question}
Return only the category name.
"""

def classify_category(q_prompt):
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=q_prompt
        )
        # Strip whitespace/newlines
        category = resp.text.strip()
        # Ensure it’s one of our categories
        return category if category in CATEGORIES else "General Knowledge"
    except:
        return "General Knowledge"

category = classify_category(category_prompt)

# --- 3) Generate AI answer ---
answer_prompt = f"""
Today is {datetime.now().strftime('%Y-%m-%d')}.
Answer the question in two sentences, then provide a deeper explanation in up to 3 short paragraphs.
Question: {question}
"""

def get_ai_response():
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=answer_prompt
        )
        return resp.text
    except:
        return "AI is currently at peak capacity. Please try again in a few minutes."

answer_text = get_ai_response()

# --- 4) Track API usage ---
# Free-tier friendly: we log a simple count of requests
usage_path = os.path.join(DATA_DIR, "api_usage.json")
os.makedirs(DATA_DIR, exist_ok=True)
usage_data = {}
if os.path.exists(usage_path):
    with open(usage_path, "r") as f:
        try: usage_data = json.load(f)
        except: pass

today_str = datetime.now().strftime("%Y-%m-%d")
usage_data[today_str] = usage_data.get(today_str, 0) + 1

with open(usage_path, "w") as f:
    json.dump(usage_data, f, indent=2)

# --- 5) Save question/answer ---
entry = {
    "timestamp": datetime.now().isoformat(),
    "question": question,
    "category": category,
    "answer": answer_text,
    "saved": False  # For UI toggle later
}

day_path = os.path.join(DATA_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.json")
day_data = []
if os.path.exists(day_path):
    with open(day_path, "r") as f:
        try: day_data = json.load(f)
        except: pass

day_data.append(entry)

with open(day_path, "w") as f:
    json.dump(day_data, f, indent=2)

print(f"Question recorded under category '{category}'. Today's API calls: {usage_data[today_str]}")
