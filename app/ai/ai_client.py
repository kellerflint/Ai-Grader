import json, os
from pathlib import Path
import requests
from dotenv import load_dotenv, set_key

from app.ai import default_settings as default
from app.ai.api_key_functions import get_api_key

load_dotenv(dotenv_path="config.env")
MODEL_OPTIONS = {
    "LLaMA 3.3 8B (Free)": "meta-llama/llama-3.3-8b-instruct:free",
    "LLaMA 3 70B (Free)": "meta-llama/llama-3-70b-instruct:free",
    "Mixtral 8x7B (Free)": "mistral/mixtral-8x7b-instruct:free",
    "Claude 3 Haiku (Free)": "anthropic/claude-3-haiku:free",
    "Gemma 7B (Free)": "google/gemma-7b-it:free",
    "OpenChat 3.5 (Free)": "openchat/openchat-3.5-0106:free"
}
def get_model_from_label(label):
    return MODEL_OPTIONS.get(label, MODEL_OPTIONS["LLaMA 3.3 8B (Free)"])


def set_model(label):
    model_id = get_model_from_label(label)
    if not model_id:
        raise ValueError("Invalid model label.")
    env_path = Path("config.env")
    set_key(env_path, "DEFAULT_MODEL", label)
    global model
    model = model_id

selected_label = os.getenv("DEFAULT_MODEL", "LLaMA 3.3 8B (Free)")
model = get_model_from_label(selected_label)
# Returns an ai client object
def ai_client():
    api_key=get_api_key()
    if not api_key:
        raise ValueError("API_KEY not found in .env file. Please add it.")
    return api_key
"""
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
        return RuntimeError(f"AI request failed: {error}")
"""
#new function to allow for dynamic selection of custom prompts
def get_ai_response(user_input: str, system_prompt: str = None):
    api_key = ai_client()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # fallback to default
    if system_prompt is None:
        from app.ai.default_settings import PROMPT as system_prompt  

    data = {
        "model" : model,
        "messages": [
            {"role": "system", "content": system_prompt},
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
        return RuntimeError(f"AI request failed: {error}")


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
        return RuntimeError(f"AI request failed: {error}")