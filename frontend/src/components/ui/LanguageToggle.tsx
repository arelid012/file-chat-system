// frontend/src/components/ui/LanguageToggle.tsx
'use client'

import React from 'react'
import { ToggleButtonGroup, ToggleButton } from '@mui/material'
import { Translate as TranslateIcon } from '@mui/icons-material'
import { useChatStore } from '@/stores/chatStore'

const LanguageToggle: React.FC = () => {
  const { language, setLanguage } = useChatStore()
  
  const handleLanguageChange = (
    event: React.MouseEvent<HTMLElement>,
    newLanguage: 'en' | 'ms'
  ) => {
    if (newLanguage !== null) {
      setLanguage(newLanguage)
    }
  }
  
  return (
    <ToggleButtonGroup
      value={language}
      exclusive
      onChange={handleLanguageChange}
      size="small"
      sx={{ 
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider'
      }}
    >
      <ToggleButton value="en">
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <TranslateIcon fontSize="small" />
          EN
        </span>
      </ToggleButton>
      <ToggleButton value="ms">
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <TranslateIcon fontSize="small" />
          MS
        </span>
      </ToggleButton>
    </ToggleButtonGroup>
  )
}

export default LanguageToggle