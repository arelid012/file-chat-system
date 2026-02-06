import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime

class VectorService:
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB with PersistentClient
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
    
    def create_chunks_and_embeddings(self, text: str, metadata: Dict[str, Any]) -> List[str]:
        """Create embeddings for text and store in vector DB"""
        # Split text into chunks
        chunks = self._chunk_text(text, chunk_size=1000, overlap=100)
        
        # Generate embeddings for each chunk
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Generate IDs
        ids = [f"{metadata['session_id']}_{i}" for i in range(len(chunks))]
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{**metadata, "chunk_index": i} for i in range(len(chunks))],
            ids=ids
        )
        
        return ids
    
    def search_similar_chunks(self, query: str, session_id: str = None, limit: int = 3) -> List[Dict]:
        """Search for relevant text chunks"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Build filter
        where_filter = {"session_id": session_id} if session_id else None
        
        # Search in vector DB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted = []
        if results['documents']:
            for i, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted.append({
                    "chunk_text": doc,
                    "filename": meta.get("filename", "Unknown"),
                    "session_id": meta.get("session_id"),
                    "score": 1 - dist
                })
        
        return formatted
    
    def delete_session_chunks(self, session_id: str):
        """Delete all embeddings for a session"""
        self.collection.delete(where={"session_id": session_id})
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Simple text chunking"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            
            if i + chunk_size >= len(words):
                break
        
        return chunks

vector_service = VectorService()