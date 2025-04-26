from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx

app = Flask(__name__)

# Directory setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
INDEX_FOLDER = "index"
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS index setup
index = None
index_file = os.path.join(INDEX_FOLDER, "faiss.index")

# Load existing index if available
if os.path.exists(index_file):
    index = faiss.read_index(index_file)
else:
    index = faiss.IndexFlatL2(768)  # Using 768 because MiniLM has 768 dimensions

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

        # Extract text from uploaded file
        text = extract_text(file_path)
        if not text.strip():
            return jsonify({"error": "Failed to extract text from the file."}), 400

        # Generate and add embeddings
        embeddings = model.encode([text])
        embeddings = np.array(embeddings).astype("float32")
        index.add(embeddings)

        # Save the FAISS index
        faiss.write_index(index, index_file)

        return jsonify({"message": "File uploaded and indexed successfully!"}), 200

# Ask endpoint
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question")
    level = data.get("level")

    if not question:
        return jsonify({"error": "No question provided."}), 400

    # Encode the question
    question_embedding = model.encode([question])
    question_embedding = np.array(question_embedding).astype("float32")

    # Check if any study material is uploaded
    if index.ntotal == 0:
        # No study material available, give general answer
        return jsonify({"answer": generate_general_answer(level)})

    # Search the FAISS index
    D, I = index.search(question_embedding, 1)

    # If similarity is very low, fallback to general answer
    if D[0][0] > 1.0:  # Higher distance means less similar
        return jsonify({"answer": generate_general_answer(level)})

    # If relevant, provide a contextual answer
    return jsonify({"answer": "Based on your uploaded study material: Here’s some information relevant to your question."})

# Extract text from uploaded file
def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error reading PDF: {e}")
    elif file_path.endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
    return text

# General answer generator
def generate_general_answer(level):
    if level == "Beginner":
        return "General info for beginners: Deep Learning (DL) is a subset of machine learning that uses neural networks with many layers."
    elif level == "Intermediate":
        return "Intermediate: Deep Learning involves training multi-layered neural networks to perform tasks such as image and speech recognition."
    elif level == "Advanced":
        return "Advanced: Deep Learning models, including convolutional and recurrent neural networks, optimize complex patterns in high-dimensional data."
    return "Here’s a general answer to your question."

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
