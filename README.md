# 📖 Context-Aware Study Assistant 

An AI-powered assistant that answers your questions **based on uploaded study material** (PDF or DOCX). If the question isn't related to the content, it can optionally give a general AI response using the Mistral LLM API.

---

## Features

-  Upload PDF or DOCX study material
-  Ask questions at various knowledge levels (Beginner, Intermediate, Advanced)
-  Context-aware response generation using Retrieval-Augmented Generation (RAG)
-  Optional support for general questions (via toggle)
-  Fast and responsive answers powered by Mistral API
-  Smart document indexing and retrieval with FAISS

---

## Technologies Used

- **Backend:** Flask
- **Frontend:** Streamlit
- **Vector Store:** FAISS
- **LLM:** Mistral API
- **RAG (Retrieval-Augmented Generation):** Used for context-aware question answering  
- **PDF & DOCX Parsing:** PyMuPDF, python-docx
- **Async File Processing:** ThreadPoolExecutor
- **Environment Management:** python-dotenv

---

## Installation

bash
# Clone the repository
git clone https://github.com/your-username/context-aware-study-assistant.git
cd context-aware-study-assistant

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment Variables
Create a .env file in the root directory:
MISTRAL_API_KEY=your_mistral_api_key_here

# Run the App
Start Flask API:
bash
python app.py

Start Streamlit Frontend:
bash
streamlit run frontend.py