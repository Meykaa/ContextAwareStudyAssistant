import os
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import docx

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ensure the OpenAI API key is available
if openai.api_key is None:
    raise ValueError("OpenAI API key not found. Please add it to the .env file.")

# Sample route for testing if the server is running
@app.route('/')
def home():
    return "Context-Aware Study Assistant is running!"

# Route to handle question-answering
@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        # Get the input data from the request
        data = request.get_json()
        question = data.get("question")
        level = data.get("level")

        if not question:
            return jsonify({"message": "No question provided."}), 400

        # Get embeddings for the question using OpenAI's API
        question_embeddings = get_openai_embeddings(question)

        # Logic for generating the answer (this can be based on your setup)
        answer = generate_answer_from_embeddings(question_embeddings, level)

        # Return the answer as a JSON response
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Route for uploading study material
@app.route('/upload', methods=['POST'])
def upload_study_material():
    try:
        # Handle file upload and indexing logic
        file = request.files.get("file")

        if file is None:
            return jsonify({"message": "No file uploaded."}), 400

        # Process the file (PDF or DOCX)
        file_content = process_file(file)

        # Index the file content (you can implement indexing logic here)
        index_file_content(file_content)

        return jsonify({"message": "Study material uploaded and indexed successfully!"})

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Helper function to get OpenAI embeddings
def get_openai_embeddings(text):
    """Get embeddings from OpenAI's API"""
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",  # You can use another model if needed
            input=text
        )
        embeddings = response['data'][0]['embedding']
        return embeddings
    except Exception as e:
        raise Exception(f"Error generating embeddings: {str(e)}")

# Helper function to generate an answer (you need to implement your own logic here)
def generate_answer_from_embeddings(embeddings, level):
    """Generate an answer based on the embeddings and knowledge level."""
    # This is a placeholder logic; implement your own logic to match embeddings with your knowledge base
    if level == "Beginner":
        return "This is a simple answer for beginners."
    elif level == "Intermediate":
        return "This answer is more detailed for intermediate learners."
    else:
        return "This is a comprehensive answer for advanced learners."

# Helper function to process PDF and DOCX files
def process_file(file):
    """Process the uploaded file (PDF or DOCX)."""
    file_extension = file.filename.split('.')[-1].lower()
    file_content = ""

    # Process PDF files
    if file_extension == "pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            file_content += page.extract_text()

    # Process DOCX files
    elif file_extension == "docx":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            file_content += para.text

    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX files are allowed.")

    return file_content

# Function to index the file content (you can implement your own indexing logic)
def index_file_content(content):
    """Index the content of the uploaded file (e.g., store it for search)."""
    # For now, we'll just simulate the indexing by printing the first 500 characters
    print("Indexing the first 500 characters of the uploaded file content:")
    print(content[:500])  # Print the first 500 characters for preview

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
