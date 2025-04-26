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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
INDEX_FOLDER = "index"
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS setup
index = None
index_file = os.path.join(INDEX_FOLDER, "faiss.index")

if os.path.exists(index_file):
    index = faiss.read_index(index_file)
else:
    index = faiss.IndexFlatL2(768)

# Upload endpoint
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

        text = extract_text(file_path)
        embeddings = model.encode([text])

        embeddings = np.array(embeddings).astype("float32")
        index.add(embeddings)

        faiss.write_index(index, index_file)

        return jsonify({"message": "File uploaded and indexed successfully!"}), 200

# Ask endpoint
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question")
    level = data.get("level")

    question_embedding = model.encode([question])

    if index.ntotal == 0:
        # No study material uploaded --> Generate natural general answer
        return jsonify({"answer": generate_general_answer(question, level)})

    question_embedding = np.array(question_embedding).astype("float32")
    D, I = index.search(question_embedding, 1)

    if D[0][0] < 0.5:
        return jsonify({"answer": generate_general_answer(question, level)})
    else:
        return jsonify({"answer": "Based on the study material, here's some information related to your question."})

def extract_text(file_path):
    # Dummy extractor for now
    return "This is the extracted text from the uploaded document."

def generate_general_answer(question, level):
    # Natural style generator
    if level == "Beginner":
        return f"{question.capitalize()} refers to fundamental concepts that are easy to understand. It usually involves basic explanations and introductory ideas."
    elif level == "Intermediate":
        return f"{question.capitalize()} involves a deeper understanding of the subject, connecting multiple concepts together and applying them in practical scenarios."
    elif level == "Advanced":
        return f"{question.capitalize()} explores complex theories, advanced methodologies, and real-world challenges related to the topic, often requiring specialized knowledge."
    return "I'm here to help! Feel free to ask anything."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
