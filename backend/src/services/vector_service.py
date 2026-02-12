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
        chunks = self._chunk_text(text, chunk_size=300, overlap=50)
        
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
        query_embedding = self.embedding_model.encode(query).tolist()
        where_filter = {"session_id": session_id} if session_id else None

        # ADD THIS
        print(f"DEBUG - Searching with session_id: {session_id}")
        print(f"DEBUG - Total chunks in collection: {self.collection.count()}")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        print(f"DEBUG - Raw results: {results['distances']}")

        formatted = []
        if results['documents']:
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                score = 1 - dist
                print(f"DEBUG chunk score: {score}")
                if score < 0.05:
                    continue
                formatted.append({
                    "chunk_text": doc,
                    "filename": meta.get("filename", "Unknown"),
                    "session_id": meta.get("session_id"),
                    "score": score
                })

        return formatted
    
    def delete_session_chunks(self, session_id: str):
        """Delete all embeddings for a session"""
        self.collection.delete(where={"session_id": session_id})   
    
    def _chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        import re

        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            word_count = len(sentence.split())
            current_chunk.append(sentence)
            current_length += word_count  # ADD FIRST, THEN CHECK

            if current_length >= chunk_size:  # flush when we hit the limit
                chunks.append(" ".join(current_chunk))
                # keep last 2 sentences as overlap for next chunk
                current_chunk = current_chunk[-2:]
                current_length = sum(len(s.split()) for s in current_chunk)

        # Don't forget remaining sentences
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        print(f"DEBUG - Created {len(chunks)} chunks")
        return chunks

vector_service = VectorService()