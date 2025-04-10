import os

# Flask App Configuration
UPLOAD_FOLDER = "data/uploads"
FAISS_INDEX_FOLDER = "data/faiss_index"
DEBUG = True  # Set to False in production

# Mistral AI API Key (Replace with your actual API key)
MISTRAL_API_KEY = "your_mistral_api_key_here"

# Embedding Model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Answer Generation Settings
DEFAULT_ANSWER_LEVEL = "intermediate"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FAISS_INDEX_FOLDER, exist_ok=True)