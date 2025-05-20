import json
from pathlib import Path
import default_settings

def load_prompts():
    try:
        with open('prompts.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"individual": default_settings.PROMPT}

def save_prompts(prompts):
    with open('prompts.json', 'w') as f:
        json.dump(prompts, f, indent=2)

def get_prompt(prompt_type="individual"):
    prompts = load_prompts()
    return prompts.get(prompt_type, default_settings.PROMPT)