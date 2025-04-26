from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from utils.pdf_loader import extract_text_from_pdf
from utils.preprocessor import split_text
from models.retrieval import retriever
from docx import Document
from concurrent.futures import ThreadPoolExecutor

# Load API key from .env or Render Environment
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY not found! Check your .env file or Render Environment.")

app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

executor = ThreadPoolExecutor(max_workers=5)
cache = {}  # In-memory cache for repeated questions

def extract_text_from_docx(file_path):
    """Extracts text from a Word (.docx) file."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def generate_answer_with_mistral(context, question, level="intermediate"):
    """Generate answer using Mistral API."""
    key = (context, question, level)
    if key in cache:
        return cache[key]

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = "You are a helpful study assistant. Only answer if the question is based on the provided study material."

    payload = {
        "model": "mistral-tiny",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Based on this study material: {context}\nAnswer this: {question}"}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        answer = result.get("choices", [{}])[0].get("message", {}).get("content", "No answer generated.")
        cache[key] = answer
        return answer
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Study Assistant API is running! Use /upload to upload files."})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        return jsonify({"error": "Only PDF and Word (.docx) files are allowed."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    def process_file():
        try:
            text = extract_text_from_pdf(file_path) if filename.endswith(".pdf") else extract_text_from_docx(file_path)
            text_chunks = split_text(text)

            if not text_chunks:
                print("❌ No text found in the document.")
                return

            retriever.build_index(text_chunks)
        except Exception as e:
            print("❌ Error while processing file:", str(e))

    executor.submit(process_file)

    return jsonify({"message": "✅ Study material is being processed and indexed in background."}), 202

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "No question provided"}), 400

    question = data["question"]
    level = data.get("level", "intermediate")
    allow_general = data.get("allow_general", True)  # default: True

    try:
        relevant_chunks = retriever.retrieve(question)
        context = " ".join(relevant_chunks[:1]).strip()

        if context and len(context) > 20:
            # 🎯 Found meaningful study material
            answer = generate_answer_with_mistral(context, question, level)
            return jsonify({"answer": answer}), 200
        else:
            # ❗ No meaningful study material → fallback
            if allow_general:
                answer = generate_answer_with_mistral("", question, level)
                return jsonify({
                    "answer": f"✅ Here's a general answer:\n\n{answer}"
                }), 200
            else:
                return jsonify({"message": "❌ No relevant study material found. Please upload study material first."}), 200

    except Exception as e:
        # ❗ Retrieval failed (probably FAISS missing)
        print(f"⚠️ Retrieval failed: {str(e)}")
        if allow_general:
            answer = generate_answer_with_mistral("", question, level)
            return jsonify({
                "answer": f"✅ Here's a general answer:\n\n{answer}"
            }), 200
        else:
            return jsonify({"message": "❌ Error retrieving study material. Please upload study material first."}), 200

if __name__ == "__main__":
    print("✅ Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
