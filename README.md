📖Context-Aware Study Assistant
An AI-powered assistant that answers your questions based on uploaded study material (PDF or DOCX).
If the study material does not contain the answer, it politely informs the user.

# Features
Upload PDF and DOCX study material

- Ask questions at various knowledge levels (Beginner, Intermediate, Advanced)

- Context-aware response generation using Retrieval-Augmented Generation (RAG)

- Only answers based on the uploaded study material (no general AI responses)

- Fast and responsive answers powered by Mistral API

- Smart document indexing and retrieval with FAISS

# Technologies Used
Backend: Flask
Frontend: Streamlit
Vector Store: FAISS
LLM: Mistral API
RAG (Retrieval-Augmented Generation): Used for context-aware question answering
PDF & DOCX Parsing: PyPDF2, python-docx
Environment Management: python-dotenv

Installation
# Clone the repository
git clone https://github.com/your-username/context-aware-study-assistant.git
cd context-aware-study-assistant

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment Variables
Create a .env file in the root directory and add:
MISTRAL_API_KEY=your_mistral_api_key_here

# Running the App
1.Start Flask Backend:
python app.py
2.Start Streamlit Frontend:
streamlit run frontend.py