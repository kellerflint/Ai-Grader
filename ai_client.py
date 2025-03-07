import os
import default_settings as default

from groq import Groq

client = Groq(
    # This is the default and can be omitted
    api_key="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"
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