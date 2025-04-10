from sentence_transformers import SentenceTransformer

# Load the embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text):
    """Convert text into an embedding vector."""
    return embedding_model.encode(text, convert_to_tensor=True)
