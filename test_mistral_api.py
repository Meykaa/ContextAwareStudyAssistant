import requests

API_KEY = "your_actual_api_key"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get("https://api.mistral.ai/v1/models", headers=headers)

print(response.json())  # Should return a list of available models