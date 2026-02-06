from fastapi import APIRouter, HTTPException
from ..models.chat import QuestionRequest, ChatResponse
from ..core.database import mongodb
from ..services.vector_service import vector_service
import requests
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=ChatResponse)
async def ask_question(question: QuestionRequest):
    try:
        # ===== Vector Search =====
        relevant_chunks = []
        context = ""
        filename = "General knowledge"
        
        if question.session_id:
            try:
                relevant_chunks = vector_service.search_similar_chunks(
                    query=question.text,
                    session_id=question.session_id,
                    limit=3
                )
                
                # Prepare context from relevant chunks
                context = "\n\n".join([chunk["chunk_text"] for chunk in relevant_chunks])
                
                if relevant_chunks:
                    filename = relevant_chunks[0]["filename"] if relevant_chunks else "Unknown"
                
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, falling back to full text")
        
        # Fallback to full text if no relevant chunks found
        if not context and question.session_id:
            file_data = await mongodb.db.files.find_one({"session_id": question.session_id})
            if file_data:
                context = file_data.get("text_content", "")[:2000]
                filename = file_data.get("filename", "Unknown")
        
        # Prepare prompt with context
        if question.language == "ms":
            prompt = f"""
            Anda adalah pembantu analisis dokumen. Jawab soalan berdasarkan konteks di bawah.
            
            DOKUMEN: {filename}
            
            KONTEKS RELEVAN:
            {context[:3000]}
            
            SOALAN: {question.text}
            
            JAWAPAN (berdasarkan konteks di atas sahaja):
            """
        else:
            prompt = f"""
            You are a document analysis assistant. Answer the question based on the context below.
            
            DOCUMENT: {filename}
            
            RELEVANT CONTEXT:
            {context[:3000]}
            
            QUESTION: {question.text}
            
            ANSWER (based only on the context above):
            """
        
        # Call Ollama
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi:latest",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                answer = response.json().get("response", "No response from AI")
            else:
                answer = f"Ollama error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            answer = "Ollama is not running. Please start it with 'ollama serve'"
        except Exception as e:
            answer = f"AI error: {str(e)}"
        
        # Prepare sources
        sources = []
        if relevant_chunks:
            for chunk in relevant_chunks[:2]:
                sources.append({
                    "source": chunk.get("filename", "Unknown"),
                    "content_preview": chunk["chunk_text"][:100] + "...",
                    "relevance_score": chunk.get("score", 0)
                })
        elif context:
            sources.append({
                "source": filename,
                "content_preview": context[:100] + "..." if context else "No content"
            })
        
        return ChatResponse(
            answer=answer,
            language=question.language,
            session_id=question.session_id,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))