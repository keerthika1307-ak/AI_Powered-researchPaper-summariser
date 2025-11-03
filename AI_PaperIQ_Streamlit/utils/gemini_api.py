import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError('Please set GOOGLE_API_KEY in .env')

def choose_best_model(preferred='auto'):
    """Choose model based on preference - using Gemini REST API"""
    if preferred == 'pro':
        return 'gemini-2.5-pro'
    elif preferred == 'flash':
        return 'gemini-2.5-flash'
    else:  # auto - prefer pro
        return 'gemini-2.5-pro'

def summarize_text(text, preferred='auto'):
    """Use Gemini REST API directly for compatibility with Python 3.8"""
    model_name = choose_best_model(preferred)
    
    prompt = f"""You are an expert AI research summarizer.

Summarize the following content clearly and concisely using the structure below:

📘 **Title:** (Give a short title related to the topic)
🧠 **Summary:** (3-5 bullet points describing key points with detailed explanation)
📊 **Insights:** (Highlight 3-4 analytical or comparative insights)
🔗 **References:** (Add any reference URLs if relevant or say 'None')

Content to summarize:
{text}"""
    
    # Use Gemini REST API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "topP": 0.95,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text from response
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            
            # Check for content with parts
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    return parts[0]['text']
            
            # Handle case where finishReason is MAX_TOKENS but no text
            finish_reason = candidate.get('finishReason', '')
            if finish_reason == 'MAX_TOKENS':
                return "[ERROR] Response truncated - text too long. Try using a shorter input or the 'flash' model."
            
            # Handle blocked content
            if finish_reason == 'SAFETY':
                return "[ERROR] Content blocked by safety filters."
        
        # Check for error in response
        if 'error' in result:
            return f"[ERROR] API error: {result['error'].get('message', str(result['error']))}"
        
        return f"[ERROR] Unexpected response format. Finish reason: {result.get('candidates', [{}])[0].get('finishReason', 'unknown')}"
        
    except requests.exceptions.RequestException as e:
        return f'[ERROR] API Request failed: {str(e)}'
    except Exception as e:
        return f'[ERROR] {str(e)}'