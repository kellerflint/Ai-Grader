import json, os
from pathlib import Path

import default_settings as default
import requests
from dotenv import load_dotenv, set_key
from api_key_functions import get_api_key

load_dotenv(dotenv_path="config.env")
MODEL_OPTIONS = {
    "LLaMA 3.3 8B (Free)": "meta-llama/llama-3.3-8b-instruct:free",
    "DeepSeek R1 Qwen3 8B (Free)": "deepseek/deepseek-r1-0528-qwen3-8b:free",
    "LLaMA 4 Maverick (Free)": "meta-llama/llama-4-maverick:free",
    "DeepSeek Chat V3 (Free)": "deepseek/deepseek-chat-v3-0324:free",
    "DeepHermes 3 (Free)": "nousresearch/deephermes-3-llama-3-8b-preview:free",
    "Mistral 7B Instruct (Free)": "mistralai/mistral-7b-instruct:free",
    "Gemma 3 4B (Free)": "google/gemma-3-4b-it:free",
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
        from default_settings import PROMPT as system_prompt  

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