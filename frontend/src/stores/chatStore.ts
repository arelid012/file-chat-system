import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sessionId?: string
}

interface FileItem {
  id: string
  session_id: string
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  created_at: string
}

interface ChatState {
  // Messages
  messages: ChatMessage[]
  currentSessionId: string | null
  language: 'en' | 'ms'
  
  // Files
  files: FileItem[]
  selectedFileId: string | null
  uploadProgress: number | null
  
  // Actions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  setMessages: (messages: ChatMessage[]) => void
  clearChat: () => void
  setLanguage: (language: 'en' | 'ms') => void
  setFiles: (files: FileItem[]) => void
  addFile: (file: FileItem) => void
  removeFile: (sessionId: string) => void
  setSelectedFile: (sessionId: string | null) => void
  setUploadProgress: (progress: number | null) => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      currentSessionId: null,
      language: 'en',
      files: [],
      selectedFileId: null,
      uploadProgress: null,
      
      addMessage: (message) => set((state) => ({
        messages: [
          ...state.messages,
          {
            ...message,
            id: Date.now().toString(),
            timestamp: new Date()
          }
        ]
      })),
      
      setMessages: (messages) => set({ messages }),
      
      clearChat: () => set({ 
        messages: [],
        currentSessionId: null 
      }),
      
      setLanguage: (language) => set({ language }),
      
      setFiles: (files) => set({ files }),
      
      addFile: (file) => set((state) => ({
        files: [...state.files, file]
      })),
      
      removeFile: (sessionId) => set((state) => ({
        files: state.files.filter(f => f.session_id !== sessionId)
      })),
      
      setSelectedFile: (sessionId) => set({ selectedFileId: sessionId }),
      
      setUploadProgress: (progress) => set({ uploadProgress: progress })
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        language: state.language,
        files: state.files
      })
    }
  )
)