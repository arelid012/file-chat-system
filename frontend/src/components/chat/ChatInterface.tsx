'use client'

import { useState } from 'react';
import { Box, TextField, Button, Paper, Typography } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import { useChatStore } from '@/stores/chatStore';
import { chatAPI } from '@/services/api';

export default function ChatInterface() {
  const [input, setInput] = useState('');
  const { messages, addMessage, selectedFileId, language } = useChatStore();
  
  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message
    addMessage({
      role: 'user',
      content: input,
      sessionId: selectedFileId || undefined,
    });
    
    // Get AI response
    try {
      const response = await chatAPI.ask(input, selectedFileId || undefined, language);
      
      addMessage({
        role: 'assistant',
        content: response.answer,
        sessionId: selectedFileId || undefined,
      });
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        role: 'assistant',
        content: 'Sorry, an error occurred. Please try again.',
        sessionId: selectedFileId || undefined,
      });
    }
    
    setInput('');
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
      {/* Messages */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
        {messages.map((msg) => (
          <Paper key={msg.id} sx={{ p: 2, mb: 1, bgcolor: msg.role === 'user' ? 'primary.light' : 'grey.100' }}>
            <Typography variant="body1">{msg.content}</Typography>
            <Typography variant="caption" color="textSecondary">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </Typography>
          </Paper>
        ))}
      </Box>
      
      {/* Input */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Ask a question about your document..."
        />
        <Button variant="contained" onClick={handleSend} disabled={!input.trim()}>
          <SendIcon />
        </Button>
      </Box>
    </Box>
  );
}