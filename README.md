# 📖 Context-Aware Study Assistant

- An AI-powered assistant that answers your questions based on uploaded study material (PDF or DOCX).
- If the material doesn't contain the answer, it politely informs the user or suggests related topics.

# ✨ Features

- Upload PDF and DOCX study materials
- Ask questions at Beginner, Intermediate, or Advanced levels
- Context-aware answers using Retrieval-Augmented Generation (RAG)
- Only answers from the uploaded material — no general web-based responses
- Fast, relevant answers powered by the Mistral API
- Smart indexing and document retrieval using FAISS

# 🛠 Technologies 

- Frontend: Streamlit
- Backend: Flask
- Vector Store: FAISS
- LLM: Mistral API
- RAG: Retrieval-Augmented Generation
- PDF & DOCX Parsing: PyPDF2, python-docx
- Environment Management: python-dotenv
- API Communication: requests

# 🚀 Installation & Running Locally

1. Clone the Repository
- git clone https://github.com/your-username/context-aware-study-assistant.git
- cd context-aware-study-assistant

2. Backend Setup
- cd backend
- python -m venv venv
- source venv/bin/activate        # Windows: venv\Scripts\activate
- pip install -r requirements.txt
- Create a .env file in the backend directory and add:
  * (MISTRAL_API_KEY=your_mistral_api_key_here)
- Start the Flask backend: 
  * python app.py

3. Frontend Setup
Open a new terminal:
- cd frontend
- python -m venv venv
- source venv/bin/activate        # Windows: venv\Scripts\activate
- pip install -r requirements.txt
- Start the Streamlit frontend:
  * streamlit run frontend.py

# 🌐 Deployment (Optional)

- Deploy backend (Flask) using Render or Docker + Gunicorn
- Deploy frontend (Streamlit) on Streamlit Community Cloud or a separate Render service
- Ensure the frontend uses the correct backend URL (update in code before deploying)

# 📎 Notes

- Works only with uploaded material — no general knowledge fallback
- “Knowledge Level” selection refines answers, but doesn't affect core document search
- Supports DOCX and PDF only (not TXT)