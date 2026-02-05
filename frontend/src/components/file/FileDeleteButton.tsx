// frontend/src/components/file/FileDeleteButton.tsx
'use client'

import React, { useState } from 'react'
import { 
  IconButton, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogContentText, 
  DialogActions,
  Button,
  CircularProgress
} from '@mui/material'
import { Delete as DeleteIcon } from '@mui/icons-material'
import { useChatStore } from '@/stores/chatStore'
import { fileAPI } from '@/services/api'

interface FileDeleteButtonProps {
  sessionId: string
}

const FileDeleteButton: React.FC<FileDeleteButtonProps> = ({ sessionId }) => {
  const [open, setOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const { removeFile, selectedFileId, setSelectedFile } = useChatStore()
  
  const handleDelete = async () => {
    try {
      setDeleting(true)
      // Call your API to delete the file
      // await fileAPI.delete(sessionId)  // Uncomment when you implement the delete endpoint
      
      // For now, just remove from local state
      removeFile(sessionId)
      
      // If deleted file was selected, clear selection
      if (selectedFileId === sessionId) {
        setSelectedFile(null)
      }
      
      setOpen(false)
    } catch (error) {
      console.error('Failed to delete file:', error)
    } finally {
      setDeleting(false)
    }
  }
  
  return (
    <>
      <IconButton
        edge="end"
        aria-label="delete"
        onClick={() => setOpen(true)}
        size="small"
        sx={{ 
          '&:hover': {
            color: 'error.main',
            bgcolor: 'error.light'
          }
        }}
      >
        <DeleteIcon fontSize="small" />
      </IconButton>
      
      <Dialog
        open={open}
        onClose={() => !deleting && setOpen(false)}
        aria-labelledby="delete-dialog-title"
      >
        <DialogTitle id="delete-dialog-title">
          Delete File?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this file? This action cannot be undone.
            Any chat history related to this file will also be removed.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setOpen(false)} 
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleDelete} 
            color="error" 
            disabled={deleting}
            startIcon={deleting ? <CircularProgress size={20} /> : null}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default FileDeleteButton