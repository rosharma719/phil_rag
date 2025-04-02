import os, requests
from dotenv import load_dotenv
load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def call_mistral_chat(prompt: str) -> str:
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "Use only the context to answer. Always cite SEP IDs if relevant."},
        {"role": "user", "content": prompt}
    ]
    data = {
        "model": "mistral-medium-2312",
        "messages": messages,
        "temperature": 0.4
    }
    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]

