import json, os
import default_settings as default
import requests
from dotenv import load_dotenv
from api_key_functions import get_api_key
model = os.getenv("OPENROUTER_MODEL","meta-llama/llama-3-70b-instruct")
# Returns an ai client object
def ai_client():
    api_key=get_api_key()
    if not api_key:
        raise ValueError("API_KEY not found in .env file. Please add it.")
    return api_key

def get_ai_response(user_input: str):
    api_key = ai_client()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model" : model,
        "messages": [
            {"role": "system", "content": default.PROMPT},
            {"role": "user", "content": user_input}
        ]
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        completions = response.json()
        return completions["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as error:
        return f"Error: {error}"


# Very similar to get_ai_response, except it works with the aggregate function
# TODO: Probably make it one function instead
def get_ai_response_2(system_prompt, user_prompt: str):
    api_key = ai_client()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model" : model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        completions = response.json()
        return completions["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as error:
        return f"Error: {error}"