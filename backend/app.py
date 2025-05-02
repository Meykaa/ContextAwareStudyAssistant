from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
from threading import Thread

# Custom utilities
from backend.utils.doc_loader import extract_text_from_docx
from backend.utils.pdf_loader import extract_text_from_pdf
from backend.utils.preprocessor import split_text
from backend.models.retrieval import retriever

# Load API key from .env file
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY not found! Check your .env file.")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def background_indexing(file_path, is_pdf):
    try:
        text = extract_text_from_pdf(file_path) if is_pdf else extract_text_from_docx(file_path)
        text_chunks = split_text(text)
        if text_chunks:
            retriever.build_index(text_chunks)
            print("✅ Background indexing completed successfully!")
        else:
            print("⚠️ No text chunks to index.")
    except Exception as e:
        print(f"❌ Background indexing failed: {e}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Study Assistant API is running!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        return jsonify({"error": "Only PDF and Word (.docx) files are allowed."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Launch background thread for indexing
    is_pdf = filename.endswith(".pdf")
    Thread(target=background_indexing, args=(file_path, is_pdf)).start()

    return jsonify({"message": "📥 File uploaded. Indexing in background..."}), 202

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "No question provided"}), 400

    question = data["question"]
    level = data.get("level", "intermediate")

    try:
        relevant_chunks = retriever.retrieve(question)
    except Exception as e:
        return jsonify({"error": "Failed to retrieve relevant info.", "details": str(e)}), 500

    if not relevant_chunks or len(relevant_chunks) == 0:
        return jsonify({
            "message": "❌ No relevant study material found for this question.",
            "suggested_topics": retriever.get_indexed_topics() if hasattr(retriever, "get_indexed_topics") else []
        }), 200

    context = " ".join(relevant_chunks).strip()
    if len(context) < 20:
        return jsonify({
            "message": "❌ Retrieved material too limited to answer meaningfully.",
            "suggested_topics": retriever.get_indexed_topics() if hasattr(retriever, "get_indexed_topics") else []
        }), 200

    try:
        answer = generate_answer_with_mistral(context, question, level)
    except Exception as e:
        return jsonify({"error": "Failed to generate answer.", "details": str(e)}), 500

    return jsonify({"answer": answer}), 200

def generate_answer_with_mistral(context, question, level="intermediate"):
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
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

if __name__ == "__main__":
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True)