from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Directory setup
UPLOAD_FOLDER = "uploads"
INDEX_FOLDER = "index"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Load lightweight Sentence Transformer model
# 🔥 Use 'paraphrase-MiniLM-L3-v2' (smaller than 'all-MiniLM-L6-v2')
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

# FAISS index setup
index = None
index_file = os.path.join(INDEX_FOLDER, "faiss.index")

if os.path.exists(index_file):
    index = faiss.read_index(index_file)
else:
    index = faiss.IndexFlatL2(384)  # Adjusted for smaller model (384 dims)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Process file
        text = extract_text(file_path)
        embeddings = model.encode([text])
        embeddings = np.array(embeddings).astype("float32")
        index.add(embeddings)

        faiss.write_index(index, index_file)
        return jsonify({"message": "File uploaded and indexed successfully!"}), 200

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question")

    question_embedding = model.encode([question])

    if index.ntotal == 0:
        return jsonify({"answer": generate_general_answer(question)})

    question_embedding = np.array(question_embedding).astype("float32")
    D, I = index.search(question_embedding, 1)

    if D[0][0] < 0.5:
        document_text = "This is the closest document to your question."
        return jsonify({"answer": document_text})
    else:
        return jsonify({"answer": generate_general_answer(question)})

def extract_text(file_path):
    return "Extracted text from uploaded file."

def generate_general_answer(question):
    return f"Here’s a general answer: {question} refers to a concept commonly used in AI or your subject area."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
