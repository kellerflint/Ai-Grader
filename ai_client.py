import default_settings as default
from dotenv import load_dotenv
from groq import Groq
from api_key_functions import get_api_key

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
    
# Very similar to get_ai_response, except it works with the aggregate function
# TODO: Probably make it one function instead
def get_ai_response_2(system_prompt, user_prompt: str):
    client = ai_client()
    print(client)
    try:
        print(system_prompt)
        print(user_prompt)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except:
        return "Error: No response. Check Settings to update your API key"