import os
import sys
import default_settings as default
from dotenv import load_dotenv
from groq import Groq
from api_key_functions import get_api_key

#bundles file pathing that allows exe to work or python command to work
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Returns an ai client object
def ai_client():
    api_key=get_api_key()
    client = Groq(api_key=api_key)
    if not api_key:
        raise ValueError("API_KEY not found in .env file. Please add it.")
    return client

def get_ai_response(user_input: str):
    client = ai_client()
    print(client)
    try:
        #print(default.PROMPT)
        #print(user_input)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": default.PROMPT
                },
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except:
        return "Error: No response. Check Settings to update your API key"