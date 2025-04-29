from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests
import os
import PyPDF2
import docx
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384
index = faiss.IndexFlatL2(dimension)
documents = []

# Root route for health check
@app.route('/')
def home():
    return '✅ Context-Aware Backend is running.'

# File reading functions
def read_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Embedding
def embed_text(text):
    return embedder.encode([text])[0]

# Mistral API call
def query_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer simply and clearly based only on the provided study material."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "top_p": 1,
        "max_tokens": 300
    }
    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Context Retrieval
def retrieve_context(question_embedding, top_k=3):
    if index.ntotal == 0:
        return []
    distances, indices = index.search(np.array([question_embedding]), top_k)
    relevant_texts = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx < len(documents) and distance < 1.0:
            relevant_texts.append(documents[idx])
    return relevant_texts

# Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    if filename.endswith('.pdf'):
        text = read_pdf(file_path)
    elif filename.endswith('.docx'):
        text = read_docx(file_path)
    elif filename.endswith('.txt'):
        text = read_txt(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    for chunk in chunks:
        emb = embed_text(chunk)
        index.add(np.array([emb]))
        documents.append(chunk)

    return jsonify({"message": "File uploaded and processed successfully!"}), 200

# Ask Route
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    question_embedding = embed_text(question)
    contexts = retrieve_context(question_embedding)

    if not contexts:
        return jsonify({"answer": "The study materials provided do not contain information about your question."}), 200

    context_text = "\n\n".join(contexts)
    prompt = f"Answer the following question based ONLY on the provided study material.\n\nStudy Material:\n{context_text}\n\nQuestion: {question}\n\nAnswer simply and clearly."

    try:
        answer = query_mistral(prompt)
        return jsonify({"answer": answer.strip()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
