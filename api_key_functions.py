import os
from dotenv import load_dotenv

ENV_FILE = "config.env"

# Load variables from the .env file
def load_api_key():
    load_dotenv(ENV_FILE, override=True) #override prevents caching
    return os.getenv("API_KEY")

# Overwrite or create .env file with the key
# TODO: original API_KEY=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
def save_api_key(api_key):
    with open(ENV_FILE, "w") as f:
        f.write(f"API_KEY={api_key.strip()}\n")

def get_api_key():
    api_key = load_api_key()
    if not api_key:
        api_key = "0"
        save_api_key(api_key)
    return api_key