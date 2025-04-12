from sentence_transformers import SentenceTransformer

def split_text(text, chunk_size=500, overlap=50):
    """Splits text into overlapping chunks for better retrieval."""
    sentences = text.split(". ")  # Split by sentences
    chunks = []
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks