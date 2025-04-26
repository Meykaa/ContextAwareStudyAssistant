from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Directory setup for uploaded files and index
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
INDEX_FOLDER = "index"
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Load pre-trained Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS index setup
index = None
index_file = os.path.join(INDEX_FOLDER, "faiss.index")

# Load existing index if available
if os.path.exists(index_file):
    index = faiss.read_index(index_file)
else:
    index = faiss.IndexFlatL2(768)  # Using a flat index for simplicity

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

        # Process the file and extract text
        text = extract_text(file_path)
        embeddings = model.encode([text])

        # Add embeddings to FAISS index
        embeddings = np.array(embeddings).astype("float32")
        index.add(embeddings)

        # Save the FAISS index to disk
        faiss.write_index(index, index_file)

        return jsonify({"message": "File uploaded and indexed successfully!"}), 200


# Ask endpoint
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question")
    level = data.get("level")

    # Generate embedding for the question
    question_embedding = model.encode([question])

    # If no study material uploaded, provide a general answer
    if index.ntotal == 0:
        return jsonify({"answer": generate_general_answer(level)})

    # Search for the most similar document in the FAISS index
    question_embedding = np.array(question_embedding).astype("float32")
    D, I = index.search(question_embedding, 1)

    if D[0][0] < 0.5:  # Arbitrary threshold for similarity
        # Get the corresponding document text (for simplicity, we'll just return the text as is)
        document_text = "This is the closest document to your question. Here's some information..."
        return jsonify({"answer": document_text})
    else:
        return jsonify({"answer": "No relevant information found. Here's a general answer."})


def extract_text(file_path):
    # Implement your PDF or DOCX text extraction logic here
    return "This is the extracted text from the uploaded document."

def generate_general_answer(level):
    # Customize answers based on the knowledge level
    if level == "Beginner":
        return "General information for beginners: Machine learning is a field of AI..."
    elif level == "Intermediate":
        return "Intermediate-level explanation of Machine Learning: Machine learning is a method of data analysis..."
    elif level == "Advanced":
        return "Advanced-level information: In machine learning, supervised learning algorithms train on labeled data..."
    return "Here's a general answer for your question."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
