// frontend/src/components/file/FileUploader.tsx
'use client'

import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload as UploadIcon } from '@mui/icons-material'
import { Box, Typography, LinearProgress, Paper } from '@mui/material'
import { useChatStore } from '@/stores/chatStore'

const FileUploader: React.FC = () => {
  const { setUploadProgress, addFile, setSelectedFile } = useChatStore()
  
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        // Update progress
        setUploadProgress(0)
        
        const response = await fetch('http://localhost:8000/api/files/upload', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`)
        }
        
        const data = await response.json()
        
        // Simulate progress (in real app, you'd track actual progress)
        setUploadProgress(100)
        
        if (data.session_id) {
          addFile({
            id: data.session_id,
            session_id: data.session_id,
            filename: file.name,
            original_filename: file.name,
            file_type: file.type.split('/')[1] || file.name.split('.').pop() || 'unknown',
            file_size: file.size,
            created_at: new Date().toISOString(),
          })
          setSelectedFile(data.session_id)
        }
        
        setTimeout(() => setUploadProgress(null), 1000)
        
      } catch (error) {
        console.error('Upload failed:', error)
        setUploadProgress(null)
      }
    }
  }, [setUploadProgress, addFile, setSelectedFile])
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  })
  
  const uploadProgress = useChatStore((state) => state.uploadProgress)
  
  return (
    <Paper
      {...getRootProps()}
      sx={{
        p: 4,
        border: '2px dashed',
        borderColor: isDragActive ? 'primary.main' : 'divider',
        bgcolor: isDragActive ? 'action.hover' : 'background.paper',
        textAlign: 'center',
        cursor: 'pointer',
        '&:hover': {
          borderColor: 'primary.main',
          bgcolor: 'action.hover',
        },
      }}
    >
      <input {...getInputProps()} />
      <UploadIcon sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
      <Typography variant="h6" gutterBottom>
        {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        Supports PDF, DOCX, TXT, Excel files (Max 50MB)
      </Typography>
      <Typography variant="caption" color="textSecondary" display="block" mt={1}>
        or click to browse files
      </Typography>
      
      {uploadProgress !== null && (
        <Box mt={3}>
          <LinearProgress 
            variant="determinate" 
            value={uploadProgress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" mt={1}>
            Uploading: {uploadProgress}%
          </Typography>
        </Box>
      )}
    </Paper>
  )
}

export default FileUploader