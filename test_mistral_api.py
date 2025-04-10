import requests

API_KEY = "your_api_key_here"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get("https://api.mistral.ai/v1/models", headers=headers)

print(response.json())  # Should return a list of available models