import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// File API
export const fileAPI = {
  upload: async (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },
  
  list: async () => {
    const response = await api.get('/files')
    return response.data
  },
  
  delete: async (sessionId: string) => {
    const response = await api.delete(`/files/${sessionId}`)
    return response.data
  },
}

// Chat API
export const chatAPI = {
  ask: async (question: string, sessionId?: string, language: 'en' | 'ms' = 'en') => {
    const response = await api.post('/chat/ask', {
      text: question,
      session_id: sessionId,
      language,
    })
    return response.data
  },
}

// System API
export const systemAPI = {
  health: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api