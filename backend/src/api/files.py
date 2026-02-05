# backend/src/api/files.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks  # Add BackgroundTasks
import os
import uuid
from datetime import datetime
from ..core.config import settings
from ..core.database import mongodb
from ..models.file import FileCreate
import aiofiles
import asyncio

router = APIRouter(prefix="/files", tags=["files"])


# Add this function right after your imports but before router definition
# In backend/src/api/files.py, add this function near the top:

async def extract_text_from_file(file_path: str, filename: str) -> str:
    """Process different file types to extract text"""
    import os
    
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()
    
    try:
        if file_extension == ".pdf":
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
            
        elif file_extension == ".txt":
            with open(file_path, "r", encoding='utf-8') as f:
                return f.read()
                
        elif file_extension == ".docx":
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
            
        elif file_extension in [".xlsx", ".xls"]:
            import pandas as pd
            df = pd.read_excel(file_path)
            text = "Excel File Contents:\n\n"
            if isinstance(df, dict):
                for sheet_name, sheet_df in df.items():
                    text += f"\nSheet: {sheet_name}\n"
                    text += sheet_df.to_string(index=False) + "\n"
            else:
                text += df.to_string(index=False)
            return text.strip()
            
        else:
            return f"Unsupported file type: {file_extension}"
            
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return f"Error processing file: {str(e)}"

# File processing function (keep this the same)
async def process_uploaded_file(file_path: str, filename: str, session_id: str):
    """Process uploaded file and store in MongoDB"""
    try:
        # Extract text based on file type
        text_content = await extract_text_from_file(file_path, filename)
        
        # Store in MongoDB
        file_data = FileCreate(
            filename=filename,
            original_filename=filename,
            file_type=filename.split('.')[-1].lower(),
            file_size=os.path.getsize(file_path),
            session_id=session_id,
            text_content=text_content
        )
        
        # Insert into MongoDB
        result = await mongodb.db.files.insert_one({
            **file_data.dict(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        print(f"✅ File processed and stored: {filename} (ID: {result.inserted_id})")
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise

# Keep extract_text_from_file function the same

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,  # Add this parameter
    file: UploadFile = File(...)
):
    """Handle file upload"""
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create uploads directory if not exists
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1]
        file_path = settings.UPLOAD_PATH / f"{session_id}{file_extension}"
        
        # Read file content
        content = await file.read()
        
        # Check file size (50MB limit)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Process file in background
        background_tasks.add_task(
            process_uploaded_file,
            str(file_path),
            file.filename,
            session_id
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "message": "File uploaded successfully. Processing in background..."
        }
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
# backend/src/api/files.py - Add this endpoint
@router.delete("/{session_id}")
async def delete_file(session_id: str):
    """Delete a file by session ID"""
    try:
        # Delete from MongoDB
        result = await mongodb.db.files.delete_one({"session_id": session_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Also delete the uploaded file if exists
        import os
        upload_dir = settings.UPLOAD_PATH
        for file in os.listdir(upload_dir):
            if file.startswith(session_id):
                os.remove(os.path.join(upload_dir, file))
                break
        
        return {"status": "success", "message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep list_files function the same