## Context-Aware Study Assistant

Context-Aware Study Assistant is an AI-powered tool that retrieves answers from uploaded study materials using Retrieval-Augmented Generation (RAG). It utilizes Mistral LLM, FAISS, Flask, and Streamlit to provide context-aware responses from PDF and DOCX files.

## Features
- Retrieves contextually relevant answers from uploaded documents.
- Supports PDF and DOCX file formats.
- Uses FAISS for efficient document search.
- Powered by Mistral LLM for intelligent responses.

## Installation
1. Clone the repository:
   git clone https://github.com/Meykaa/ContextAwareStudyAssistant.git

2. Navigate to the project directory:
   cd ContextAwareStudyAssistant

3. Create and activate a virtual environment:
  - Windows:
   python -m venv venv
   venv\Scripts\Activate
  
  - Mac/Linux:
   python3 -m venv venv
   source venv/bin/activate

4. Install dependencies:
   pip install -r requirements.txt


5. Set up the environment variables:
- Create a `.env` file in the project directory and add your **Mistral API Key**:
  
  MISTRAL_API_KEY=your_api_key_here
  
6. Run the application:
   -Start the Backend
   Run the Flask backend server:
   python backend.py

   -Start the Frontend
   Run the Streamlit UI:
   streamlit run frontend.py


## Usage
- Upload a PDF or DOCX file.
- Enter a question, and the assistant will provide context-aware answers.

