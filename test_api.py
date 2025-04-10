import requests

url = "http://127.0.0.1:5000/ask"
headers = {"Content-Type": "application/json"}
data = {
    "question": "What is machine learning?",
    "level": "beginner"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())