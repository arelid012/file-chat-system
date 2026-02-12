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
                        
                if relevant_chunks:
                    filename = relevant_chunks[0]["filename"] if relevant_chunks else "Unknown"
                
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, falling back to full text")

        # HARD STOP if no context found for selected file
        if question.session_id and not relevant_chunks:
            return ChatResponse(
                answer=(
                    "I can't find any readable content for the selected file yet. "
                    "It may still be processing or the document has no extractable text."
                ),
                language=question.language,
                session_id=question.session_id,
                sources=[]
            )

        # Filter by quality FIRST
        high_quality_chunks = [c for c in relevant_chunks if c.get("score", 0) >= 0.05]

        if question.session_id and not high_quality_chunks:
            return ChatResponse(
                answer="I couldn't find relevant information in the document to answer this question.",
                language=question.language,
                session_id=question.session_id,
                sources=[]
            )

        # THEN build context from high quality chunks only
        context = "\n\n".join([chunk["chunk_text"] for chunk in high_quality_chunks])

        # THEN truncate
        max_context_chars = 3500
        truncated = context[:max_context_chars]
        truncation_note = "\n[NOTE: Context was truncated due to length.]" if len(context) > max_context_chars else ""

        # Prepare prompt with context
        if question.language == "ms":
            prompt = f"""
            Anda adalah pembantu analisis dokumen. Jawab soalan berdasarkan konteks di bawah.
            
            DOKUMEN: {filename}
            
            KONTEKS RELEVAN:
            {truncated}{truncation_note}
            
            SOALAN: {question.text}
            
            JAWAPAN (berdasarkan konteks di atas sahaja):
            """
        else:
            prompt = f"""
            SYSTEM ROLE:
            You are a strict document analysis assistant used in production software.

            PRIMARY OBJECTIVE:
            Answer the user's question using ONLY the provided document context.

            NON-NEGOTIABLE RULES:
            1. Use ONLY facts explicitly stated in the context.
            2. Do NOT infer, assume, guess, or generalize.
            3. Do NOT add titles, qualifications, dates, or explanations unless explicitly written.
            4. If the information is missing, unclear, or not stated, respond EXACTLY with:
            "I cannot find this information in the document."
            5. If the context contains repeated or corrupted text, acknowledge it and summarize cautiously.
            6. NEVER use outside knowledge.

            SELF-CHECK BEFORE ANSWERING:
            - Can every sentence in my answer be directly traced to the context?
            - If not, I must refuse.

            DOCUMENT NAME:
            {filename}

            DOCUMENT CONTEXT:
            <<<BEGIN CONTEXT>>>
            {truncated}{truncation_note}
            <<<END CONTEXT>>>

            USER QUESTION:
            {question.text}

            FINAL ANSWER:
            (Answer clearly and concisely. No extra explanations.)
            """
        
        # Call Ollama
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral:latest",  # or llama3.2
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # ADD THIS: lower temp = less creativity = less hallucination
                        "top_p": 0.9
                    }
                },
                timeout=60  # mistral needs more time
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