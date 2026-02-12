// frontend/src/components/file/FileList.tsx
'use client'

import React from 'react'
import { 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Typography,
  Box,
  Chip,
  Paper
} from '@mui/material'
import { 
  Description as FileIcon, 
  CheckCircle as SelectedIcon
} from '@mui/icons-material'
import { useChatStore } from '@/stores/chatStore'
import FileDeleteButton from './FileDeleteButton'

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const FileList: React.FC = () => {
  const { files, selectedFileId, setSelectedFile, clearChat } = useChatStore()

  
  if (files.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
        <Typography variant="body2" color="textSecondary">
          No files uploaded yet
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Upload a document to start chatting
        </Typography>
      </Paper>
    )
  }
  
  return (
    <List sx={{ maxHeight: 300, overflow: 'auto' }}>
      {files.map((file) => (
        <ListItem
          key={file.session_id}
          secondaryAction={
            <FileDeleteButton sessionId={file.session_id} />
          }
          sx={{
            bgcolor: selectedFileId === file.session_id ? 'action.selected' : 'transparent',
            borderRadius: 1,
            mb: 1,
            '&:hover': {
              bgcolor: 'action.hover',
              cursor: 'pointer'
            }
          }}
          onClick={() => {
            clearChat()
            setSelectedFile(file.session_id)
          }}
        >
          <ListItemIcon>
            {selectedFileId === file.session_id ? (
              <SelectedIcon color="primary" />
            ) : (
              <FileIcon />
            )}
          </ListItemIcon>
          <ListItemText
            primary={
              <Typography variant="body2" noWrap component="div"> {/* Add component="div" */}
                {file.filename}
              </Typography>
            }
            secondary={
              // FIX: Wrap secondary content in a div, not a Typography
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }} component="div">
                <Chip 
                  label={file.file_type?.toUpperCase() || 'FILE'} 
                  size="small" 
                  variant="outlined"
                />
                <Typography variant="caption" color="textSecondary" component="span">
                  {formatFileSize(file.file_size)}
                </Typography>
                <Typography variant="caption" color="textSecondary" component="span">
                  {new Date(file.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            }
            disableTypography // Add this to prevent automatic Typography wrapper
          />
        </ListItem>
      ))}
    </List>
  )
}

export default FileList