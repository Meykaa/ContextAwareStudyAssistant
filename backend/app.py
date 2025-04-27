from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import faiss
import numpy as np
import openai
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Directory setup
UPLOAD_FOLDER = "uploads"
INDEX_FOLDER = "index"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# Load lightweight Sentence Transformer model
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

# Set up FAISS index
index = None
index_file = os.path.join(INDEX_FOLDER, "faiss.index")

if os.path.exists(index_file):
    index = faiss.read_index(index_file)
else:
    index = faiss.IndexFlatL2(384)  # 384 dimensions for this model

# Set OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

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

        # Extract text from the file
        text = extract_text(file_path)
        embeddings = model.encode([text])
        embeddings = np.array(embeddings).astype("float32")
        index.add(embeddings)

        # Save the updated FAISS index
        faiss.write_index(index, index_file)

        return jsonify({"message": "File uploaded and indexed successfully!"}), 200

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    question_embedding = model.encode([question])

    if index.ntotal == 0:
        # No study material uploaded: Use OpenAI to generate a good answer
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert study assistant."},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            max_tokens=300
        )
        answer = response['choices'][0]['message']['content'].strip()
        return jsonify({"answer": answer})

    # Study material available: Use FAISS to search
    question_embedding = np.array(question_embedding).astype("float32")
    D, I = index.search(question_embedding, 1)

    if D[0][0] < 0.5:
        document_text = "This is the closest document to your question."
        return jsonify({"answer": document_text})
    else:
        # If no good match found, fallback to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert study assistant."},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            max_tokens=300
        )
        answer = response['choices'][0]['message']['content'].strip()
        return jsonify({"answer": answer})

def extract_text(file_path):
    # TODO: Implement real PDF/DOCX text extraction
    return "Extracted text from the uploaded document."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
