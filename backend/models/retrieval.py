import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

# Define FAISS index storage path
INDEX_PATH = "data/faiss_index/index.bin"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load embedding model
model = SentenceTransformer(MODEL_NAME)

class Retriever:
    def __init__(self):
        self.index = None
        self.chunks = []
        self.dimension = None
        self.load_index()

    def build_index(self, chunks):
        """Builds a FAISS index from text chunks."""
        if not chunks:
            raise ValueError("No documents provided for indexing.")
        
        embeddings = model.encode(chunks, convert_to_numpy=True)
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
        self.chunks = chunks
        
        # Save index
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)
        
        # Save chunks for retrieval
        with open(INDEX_PATH.replace(".bin", "_chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)
        
        print("Index built and saved successfully!")

    def load_index(self):
        """Loads the FAISS index if it exists."""
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(INDEX_PATH.replace(".bin", "_chunks.pkl"), "rb") as f:
                self.chunks = pickle.load(f)
            print("FAISS index loaded successfully!")
        else:
            print("No existing index found. Please upload study material first.")

    def retrieve(self, query, top_k=3):
        """Retrieves top_k most relevant chunks based on query."""
        if self.index is None or not self.chunks:
            raise RuntimeError("FAISS index not found. Please upload study material first.")
        
        query_embedding = model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]
        return results

retriever = Retriever()