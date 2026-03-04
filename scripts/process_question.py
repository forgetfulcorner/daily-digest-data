import re # Add this to your imports at the top

def get_ai_response():
    # Use Gemma 3 27B-it as primary
    model_id = "gemma-3-27b-it"
    
    prompt = f"""
    Return a JSON object for: "{question_input}"
    1. clean_question: Professional rephrase.
    2. category: [Science, Tech, History, Culture, Nature, General].
    3. answer: 3-paragraph explanation.
    
    IMPORTANT: Return ONLY the raw JSON. No conversational text.
    {{
      "clean_question": "...",
      "category": "...",
      "answer": "..."
    }}
    """

    try:
        # NOTICE: We removed 'config' entirely for Gemma
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        # Gemma often wraps JSON in markdown blocks (```json ... ```)
        # This regex strips those away so json.loads doesn't crash
        raw_text = response.text
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return json.loads(raw_text)

    except Exception as e:
        print(f"Gemma failed: {e}. Falling back to Gemini...")
        # Your existing Gemini fallback code...
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
