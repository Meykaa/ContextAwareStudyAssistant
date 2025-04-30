from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Custom utilities
from utils.doc_loader import extract_text_from_docx
from utils.pdf_loader import extract_text_from_pdf
from utils.preprocessor import split_text
from models.retrieval import retriever

# Load API key from .env file
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY not found! Check your .env file.")

app = Flask(__name__)

# Define upload folder
UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_answer_with_mistral(context, question, level="intermediate"):
    """Uses Mistral API to generate an answer from the retrieved context."""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-tiny",
        "messages": [
            {"role": "system", "content": f"You are a helpful study assistant providing {level}-level answers."},
            {"role": "user", "content": f"Based on this study material: {context}\nAnswer this: {question}"}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No answer generated.")
    except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
        return f"⚠️ API Error: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    """Home route to confirm API is running."""
    return jsonify({"message": "Study Assistant API is running! Use /upload to upload files."})

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload (PDF or DOCX) and indexing."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        return jsonify({"error": "Only PDF and Word (.docx) files are allowed."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_docx(file_path)
        
        text_chunks = split_text(text)
    except Exception as e:
        return jsonify({"error": "Failed to process the file.", "details": str(e)}), 500

    if not text_chunks:
        return jsonify({"error": "No text found in the document."}), 400

    try:
        retriever.build_index(text_chunks)
    except Exception as e:
        return jsonify({"error": "Failed to index document.", "details": str(e)}), 500

    return jsonify({"message": "✅ Study material uploaded and indexed successfully!"}), 200

@app.route("/ask", methods=["POST"])
def ask_question():
    """Answer user questions based on indexed study material."""
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "No question provided"}), 400

    question = data["question"]
    level = data.get("level", "intermediate")

    try:
        relevant_chunks = retriever.retrieve(question)
    except Exception as e:
        return jsonify({"error": "Failed to retrieve relevant information.", "details": str(e)}), 500

    if not relevant_chunks or len(relevant_chunks) == 0:
        return jsonify({
            "message": "❌ No relevant study material found for this question."
        }), 200

    context = " ".join(relevant_chunks).strip()

    if len(context) < 20:
        return jsonify({
            "message": "❌ The retrieved study material is too limited to provide a meaningful answer."
        }), 200

    try:
        answer = generate_answer_with_mistral(context, question, level)
    except Exception as e:
        return jsonify({"error": "Failed to generate an answer.", "details": str(e)}), 500

    return jsonify({"answer": answer}), 200

if __name__ == "__main__":
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

    app.run(debug=True)
