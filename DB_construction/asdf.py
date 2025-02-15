import requests

API_KEYS = [
    "Ti4v1xEM5LGb7q45msVrbyCuHVptbzbx",
    "iPr4q8cSuQMYYrZOdPgBw0IA2TpGxUxC",
    "sMnUeF5GwZluJOIXKoeZJuqdzpm9WQW8"
]

url = "https://api.mistral.ai/v1/chat/completions"

data = {
    "model": "mistral-medium-2312",
    "messages": [
        {"role": "system", "content": "Test request to validate API keys."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.4
}

for key in API_KEYS:
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"API Key: {key[-4:]} → {response.status_code} {response.text}")
