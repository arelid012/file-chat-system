from fastapi import APIRouter, HTTPException
from ..models.chat import QuestionRequest, ChatResponse
from ..core.database import mongodb
import requests
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=ChatResponse)
async def ask_question(question: QuestionRequest):
    try:
        # If session_id provided, get file text from MongoDB
        file_text = ""
        filename = "General knowledge"
        
        if question.session_id:
            # Find file in MongoDB
            file_data = await mongodb.db.files.find_one({"session_id": question.session_id})
            if file_data:
                file_text = file_data.get("text_content", "")
                filename = file_data.get("filename", "Unknown")
        
        # Prepare prompt based on language
        if question.language == "ms":  # Malay
            prompt = f"""
            Anda adalah pembantu analisis dokumen. Jawab soalan pengguna berdasarkan kandungan dokumen.
            
            DOKUMEN: {filename}
            KANDUNGAN: {file_text[:3000] if file_text else "Tiada dokumen dimuat naik"}
            
            SOALAN: {question.text}
            
            JAWAPAN:
            """
        else:  # English
            prompt = f"""
            You are a document analysis assistant. Answer the user's question based on the document content.
            
            DOCUMENT: {filename}
            CONTENT: {file_text[:3000] if file_text else "No document uploaded"}
            
            QUESTION: {question.text}
            
            ANSWER:
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
        
        return ChatResponse(
            answer=answer,
            language=question.language,
            session_id=question.session_id,
            sources=[{"source": filename, "content_preview": file_text[:100] + "..." if file_text else "No content"}]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))