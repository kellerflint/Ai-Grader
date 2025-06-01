import os
import json
from platformdirs import user_data_dir

APP_NAME = "AI-Grader"
PROMPT_FILE = os.path.join(user_data_dir(APP_NAME), "saved_prompts.json")
AGGREGATE_PROMPT_FILE = os.path.join(user_data_dir(APP_NAME), "aggregate_prompts.json")

#Individual
def save_prompt(new_prompt):
    os.makedirs(os.path.dirname(PROMPT_FILE), exist_ok=True)
    try:
        prompts = load_prompts()

        # Avoid duplicate names
        for prompt in prompts:
            if prompt["name"] == new_prompt["name"]:
                prompt["content"] = new_prompt["content"]
                break
        else:
            prompts.append(new_prompt)

        with open(PROMPT_FILE, "w") as f:
            json.dump(prompts, f, indent=2)
    except Exception as e:
        print("Error saving prompt:", e)

def load_prompts():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r") as f:
            return json.load(f)
    return []

#Aggregate
def save_aggregate_prompt(new_prompt):
    os.makedirs(os.path.dirname(AGGREGATE_PROMPT_FILE), exist_ok=True)
    try:
        prompts = load_aggregate_prompts()

        for prompt in prompts:
            if prompt["name"] == new_prompt["name"]:
                prompt["content"] = new_prompt["content"]
                break
        else:
            prompts.append(new_prompt)

        with open(AGGREGATE_PROMPT_FILE, "w") as f:
            json.dump(prompts, f, indent=2)
    except Exception as e:
        print("Error saving aggregate prompt:", e)

def load_aggregate_prompts():
    if os.path.exists(AGGREGATE_PROMPT_FILE):
        with open(AGGREGATE_PROMPT_FILE, "r") as f:
            return json.load(f)
    return []
