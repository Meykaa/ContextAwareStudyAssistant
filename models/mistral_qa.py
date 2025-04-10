import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY not found! Check your .env file.")

def generate_answer(context, question, level="intermediate"):
    """Uses Mistral API to generate an answer from retrieved study material."""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-tiny",  # Change to "mistral-7B" or "mixtral-8x7B" if needed
        "messages": [
            {"role": "system", "content": f"You are a helpful study assistant providing {level}-level answers."},
            {"role": "user", "content": f"Based on this study material: {context}\nAnswer this: {question}"}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No answer generated.")
    else:
        raise Exception(f"Mistral API Error: {response.status_code} - {response.text}")
