import os
from dotenv import load_dotenv
import requests
import json
import time
import random
from datetime import datetime, timedelta

try:
    import streamlit as st
except Exception:
    st = None

load_dotenv()

API_KEY = os.getenv('GROQ_API_KEY')
if not API_KEY and st is not None:
    try:
        API_KEY = st.secrets.get('GROQ_API_KEY', None)
    except Exception:
        API_KEY = None

if not API_KEY:
    raise ValueError('Please set GROQ_API_KEY in .env or Streamlit secrets')

# Global rate limiting tracker and cache
_last_request_time = None
_request_count = 0
_request_times = []
_MIN_REQUEST_INTERVAL = 1  # Groq is faster, 1 second between requests
_MAX_REQUESTS_PER_MINUTE = 30  # Groq free tier limit
_response_cache = {}  # Cache API responses to avoid duplicate calls

def _check_rate_limit():
    """
    Check and enforce rate limiting before making requests.
    Returns: (allowed: bool, wait_time: float)
    """
    global _last_request_time, _request_count, _request_times
    
    current_time = datetime.now()
    
    # Clean up old request times (older than 1 minute)
    _request_times = [t for t in _request_times if current_time - t < timedelta(minutes=1)]
    
    # Check if we've hit the per-minute limit
    if len(_request_times) >= _MAX_REQUESTS_PER_MINUTE:
        oldest_request = min(_request_times)
        wait_until = oldest_request + timedelta(minutes=1)
        wait_seconds = (wait_until - current_time).total_seconds()
        if wait_seconds > 0:
            return False, wait_seconds
    
    # Check minimum interval between requests
    if _last_request_time:
        time_since_last = (current_time - _last_request_time).total_seconds()
        if time_since_last < _MIN_REQUEST_INTERVAL:
            return False, _MIN_REQUEST_INTERVAL - time_since_last
    
    return True, 0

def _record_request():
    """Record that a request was made"""
    global _last_request_time, _request_times
    _last_request_time = datetime.now()
    _request_times.append(datetime.now())

def choose_best_model(preferred='auto'):
    """Choose model based on preference - using Groq API"""
    # Using current active Groq models (updated Dec 2024)
    if preferred == 'pro':
        return 'llama-3.3-70b-versatile'  # Most capable model
    elif preferred == 'flash':
        return 'llama-3.1-8b-instant'  # Fastest model
    else:  # auto - prefer the best available
        return 'llama-3.3-70b-versatile'  # Default to most capable

def make_groq_request(model_name, prompt, max_tokens=2048, use_cache=True):
    """
    Centralized function to make Groq API requests with retry logic and rate limiting
    
    Args:
        model_name: The Groq model to use
        prompt: The prompt text
        max_tokens: Maximum tokens in response
        use_cache: If True, return cached response for identical requests
    """
    # Generate cache key
    import hashlib
    cache_key = hashlib.md5(f"{model_name}:{prompt}".encode()).hexdigest()
    
    # Check cache first
    if use_cache and cache_key in _response_cache:
        print("✓ Using cached response")
        return _response_cache[cache_key]
    
    # Check rate limit before making request
    allowed, wait_time = _check_rate_limit()
    if not allowed:
        print(f"⏳ Rate limit: waiting {wait_time:.1f} seconds before request...")
        time.sleep(wait_time)
    
    # Record this request
    _record_request()
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "top_p": 0.95,
    }
    
    max_retries = 3
    base_delay = 2  # Base delay for retries
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            status = response.status_code
            
            # Handle rate limiting
            if status in (429, 503):
                if attempt == max_retries:
                    raise Exception(f"⚠️ Rate limit exceeded. Your API quota may be exhausted.\n\n"
                                    f"Solutions:\n"
                                    f"1. Wait 60 seconds and try again\n"
                                    f"2. Check your quota at: https://console.groq.com/\n"
                                    f"3. Consider upgrading for higher limits")
                
                # Calculate exponential backoff with jitter
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        sleep_s = int(retry_after)
                    except ValueError:
                        sleep_s = base_delay * (2 ** attempt) + random.uniform(0, 2)
                else:
                    sleep_s = base_delay * (2 ** attempt) + random.uniform(0, 2)
                
                print(f"⏳ Rate limited. Waiting {sleep_s:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(sleep_s)
                continue
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response text (OpenAI-compatible format)
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                
                if 'message' in choice and 'content' in choice['message']:
                    response_text = choice['message']['content'].strip()
                    
                    # Cache the response
                    if use_cache:
                        _response_cache[cache_key] = response_text
                    
                    return response_text
                
                # Handle different finish reasons
                finish_reason = choice.get('finish_reason', '')
                if finish_reason == 'length':
                    raise Exception("Response truncated - text too long. Try using shorter input.")
                elif finish_reason == 'content_filter':
                    raise Exception("Content blocked by safety filters.")
            
            # Check for API error in response
            if 'error' in result:
                error_msg = result['error'].get('message', str(result['error']))
                raise Exception(f"API error: {error_msg}")
            
            # Unexpected format
            raise Exception(f"Unexpected response format. Response: {json.dumps(result)[:200]}")
        
        except requests.exceptions.Timeout:
            if attempt == max_retries:
                raise Exception("Request timed out after multiple attempts.")
            sleep_s = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Timeout. Retrying in {sleep_s:.2f} seconds...")
            time.sleep(sleep_s)
        
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                status_info = ''
                try:
                    if hasattr(e, 'response') and e.response is not None:
                        status_info = f" (status {e.response.status_code})"
                        # Try to get error details from response
                        try:
                            error_detail = e.response.json()
                            if 'error' in error_detail:
                                status_info += f": {error_detail['error'].get('message', '')}"
                        except:
                            pass
                except:
                    pass
                raise Exception(f"API Request failed{status_info}")
            
            sleep_s = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Request failed. Retrying in {sleep_s:.2f} seconds...")
            time.sleep(sleep_s)

def summarize_text(text, preferred='auto'):
    """Use Groq API to summarize text"""
    model_name = choose_best_model(preferred)
    
    # Truncate text if too long (approximate token limit)
    max_chars = 30000  # Groq handles more tokens
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Content truncated due to length...]"
    
    prompt = f"""You are an expert AI research summarizer. Summarize the following content clearly and concisely using the structure below:

📘 **Title:** (Give a short title related to the topic)

🧠 **Summary:** (3-5 bullet points describing key points with detailed explanation)

📊 **Insights:** (Highlight 3-4 analytical or comparative insights)

🔗 **References:** (Add any reference URLs if relevant or say 'None')

Content to summarize:
{text}"""
    
    try:
        # Rate limiting is now handled inside make_groq_request
        return make_groq_request(model_name, prompt, max_tokens=2048)
    except Exception as e:
        return f"[ERROR] {str(e)}"

def generate_chat_response(prompt, model_name='flash'):
    """
    Generate a conversational response using Groq API
    
    Args:
        prompt: User's question with context
        model_name: 'flash' for faster responses, 'pro' for detailed
    
    Returns:
        str: AI-generated response
    """
    model = choose_best_model(model_name)
    
    # Enhanced prompt for clearer responses
    enhanced_prompt = f"""You are a helpful AI assistant specialized in explaining technical concepts clearly and concisely.

Guidelines for your response:
- Be direct and to the point
- Use clear, simple language
- Break down complex topics into digestible parts
- Use bullet points or numbered lists when appropriate
- Include examples when helpful
- Keep responses well-structured and easy to read

User's question:
{prompt}

Provide a clear, well-organized response:"""
    
    try:
        # Rate limiting is now handled inside make_groq_request
        return make_groq_request(model, enhanced_prompt, max_tokens=2048)
    except Exception as e:
        raise Exception(f"Chat generation failed: {str(e)}")

# Optional: Add a function to test API connectivity
def test_api_connection():
    """Test if the API key works and check quota"""
    try:
        model = 'llama-3.1-8b-instant'
        result = make_groq_request(model, "Say 'API connection successful!'", max_tokens=50)
        return True, result
    except Exception as e:
        return False, str(e)

# Optional: Clear cache
def clear_cache():
    """Clear the response cache"""
    global _response_cache
    _response_cache = {}
    print("✓ Cache cleared")

# Optional: Check cache size
def get_cache_info():
    """Get information about the cache"""
    return {
        'cached_responses': len(_response_cache),
        'cache_keys': list(_response_cache.keys())[:5]  # Show first 5
    }

def get_rate_limit_status():
    """Get current rate limiting status"""
    global _request_times
    current_time = datetime.now()
    
    # Clean up old requests
    _request_times = [t for t in _request_times if current_time - t < timedelta(minutes=1)]
    
    requests_in_last_minute = len(_request_times)
    remaining = max(0, _MAX_REQUESTS_PER_MINUTE - requests_in_last_minute)
    
    if _last_request_time:
        seconds_since_last = (current_time - _last_request_time).total_seconds()
        next_available = max(0, _MIN_REQUEST_INTERVAL - seconds_since_last)
    else:
        next_available = 0
    
    return {
        'requests_last_minute': requests_in_last_minute,
        'remaining_in_minute': remaining,
        'seconds_until_next_available': next_available
    }

def list_available_models():
    """
    List all available Groq models
    Useful for debugging model availability issues
    """
    url = "https://api.groq.com/openai/v1/models"
    
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        models = []
        if 'data' in data:
            for model in data['data']:
                model_id = model.get('id', '')
                models.append(model_id)
        
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []