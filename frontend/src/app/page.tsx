// frontend/src/app/page.tsx (CSS Grid - NO MUI Grid issues!)
'use client'

import { Container, Paper, Typography, Box, Divider } from '@mui/material'
import FileUploader from '@/components/file/FileUploader'
import ChatInterface from '@/components/chat/ChatInterface'
import FileList from '@/components/file/FileList'
import LanguageToggle from '@/components/ui/LanguageToggle'
import { useChatStore } from '@/stores/chatStore'

export default function Home() {
  const { selectedFileId, files } = useChatStore()
  
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          📄 File Chat System
        </Typography>
        <Typography variant="h6" color="textSecondary" paragraph>
          Upload documents and chat with AI about their content
        </Typography>
      </Box>
      
      {/* REPLACED Grid with simple CSS Grid */}
      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' },
        gap: 3,
        alignItems: 'start'
      }}>
        {/* Left Sidebar */}
        <Box>
          <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              📤 Upload Document
            </Typography>
            <FileUploader />
            
            <Divider sx={{ my: 3 }} />
            
            <Typography variant="h6" gutterBottom>
              📁 Your Files ({files.length})
            </Typography>
            <FileList />
            
            {selectedFileId && (
              <Box sx={{ mt: 3, p: 2, bgcolor: 'action.selected', borderRadius: 1 }}>
                <Typography variant="caption">
                  Selected: {files.find(f => f.session_id === selectedFileId)?.filename}
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
        
        {/* Main Chat Area */}
        <Box>
          <Paper sx={{ 
            p: 3, 
            height: 'calc(100vh - 160px)', 
            display: 'flex', 
            flexDirection: 'column'
          }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 3 
            }}>
              <Box>
                <Typography variant="h6">
                  💬 Document Chat
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Ask questions about your uploaded documents
                </Typography>
              </Box>
              <LanguageToggle />
            </Box>
            
            <ChatInterface />
            
            <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="caption" color="textSecondary">
                {selectedFileId 
                  ? `Chatting with: ${files.find(f => f.session_id === selectedFileId)?.filename}`
                  : 'No file selected - AI will use general knowledge'
                }
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Box>
    </Container>
  )
}