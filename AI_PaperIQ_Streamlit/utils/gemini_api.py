import os
from dotenv import load_dotenv
import requests
import json
import time
import random
try:
    import streamlit as st
except Exception:
    st = None

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY and st is not None:
    try:
        API_KEY = st.secrets.get('GOOGLE_API_KEY', None)
    except Exception:
        API_KEY = None
if not API_KEY:
    raise ValueError('Please set GOOGLE_API_KEY in .env or Streamlit secrets')

def choose_best_model(preferred='auto'):
    """Choose model based on preference - using Gemini REST API"""
    if preferred == 'pro':
        return 'gemini-2.0-flash'
    elif preferred == 'flash':
        return 'gemini-2.0-flash'
    else:  # auto - prefer flash (stable and fast)
        return 'gemini-2.0-flash'

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
        last_status = None
        max_retries = 4
        response = None
        for attempt in range(max_retries + 1):
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            last_status = response.status_code
            if last_status in (429, 503):
                if attempt == max_retries:
                    break
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        sleep_s = int(retry_after)
                    except ValueError:
                        sleep_s = 1 + random.uniform(0, 0.25)
                else:
                    sleep_s = min(2 ** attempt, 16) + random.uniform(0, 0.25)
                time.sleep(sleep_s)
                continue
            response.raise_for_status()
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text']
                finish_reason = candidate.get('finishReason', '')
                if finish_reason == 'MAX_TOKENS':
                    return "[ERROR] Response truncated - text too long. Try using a shorter input or the 'flash' model."
                if finish_reason == 'SAFETY':
                    return "[ERROR] Content blocked by safety filters."
            if 'error' in result:
                return f"[ERROR] API error: {result['error'].get('message', str(result['error']))}"
            return f"[ERROR] Unexpected response format. Finish reason: {result.get('candidates', [{}])[0].get('finishReason', 'unknown')}"
        if last_status in (429, 503):
            return "[ERROR] Rate limit or service unavailable. Please wait a moment and try again."
        return "[ERROR] API Request failed."
        
    except requests.exceptions.RequestException as e:
        status = ''
        try:
            if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'status_code'):
                status = f" (status {e.response.status_code})"
        except Exception:
            status = ''
        return f"[ERROR] API Request failed{status}. Please try again later."
    except Exception as e:
        return f'[ERROR] {str(e)}'