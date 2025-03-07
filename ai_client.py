import os
import default_settings as default
from dotenv import load_dotenv 
load_dotenv(dotenv_path='./config.env')

from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
print(api_key)

client = Groq(
    api_key=api_key
)

def get_ai_response(user_input: str):
    try:
        print(default.PROMPT)
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
        return "Error"