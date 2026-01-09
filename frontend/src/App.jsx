import React, { useState, useRef, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import LogUpload from './components/LogUpload'
import './App.css'

function App() {
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem('sessionId') || null
  })

  useEffect(() => {
    if (!sessionId) {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      setSessionId(newSessionId)
      localStorage.setItem('sessionId', newSessionId)
    }
  }, [sessionId])

  return (
    <div className="app">
      <div className="app-container">
        <header className="app-header">
          <h1>🔍 Intelligent RCA Chatbot</h1>
          <p>AI-Powered Log Analysis & Root Cause Analysis</p>
        </header>
        
        <div className="app-content">
          <div className="sidebar">
            <LogUpload sessionId={sessionId} />
          </div>
          
          <div className="main-content">
            <ChatInterface sessionId={sessionId} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App


