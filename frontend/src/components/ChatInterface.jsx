import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Send, Loader2 } from 'lucide-react'
import './ChatInterface.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ChatInterface({ sessionId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const [streamingMessage, setStreamingMessage] = useState('')

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingMessage])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)
    setStreamingMessage('')

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      // Try streaming first
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      })

      if (response.ok) {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let fullResponse = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              fullResponse += data
              setStreamingMessage(fullResponse)
            }
          }
        }

        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: fullResponse 
        }])
        setStreamingMessage('')
      } else {
        throw new Error('Streaming failed, trying regular request')
      }
    } catch (error) {
      console.error('Streaming error:', error)
      
      // Fallback to regular request
      try {
        const response = await axios.post(`${API_BASE_URL}/api/chat`, {
          message: userMessage,
          session_id: sessionId,
        })

        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: response.data.response,
          sources: response.data.sources 
        }])
      } catch (err) {
        console.error('Error sending message:', err)
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Error: ${err.response?.data?.detail || err.message}` 
        }])
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome to RCA Chatbot</h2>
            <p>Ask me questions about your logs to perform root cause analysis.</p>
            <p>Example questions:</p>
            <ul>
              <li>"What errors occurred in the last hour?"</li>
              <li>"Analyze the connection timeout issues"</li>
              <li>"What's causing the high memory usage?"</li>
            </ul>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'user' ? (
                <p>{msg.content}</p>
              ) : (
                <div>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      <strong>Sources:</strong>
                      {msg.sources.map((source, i) => (
                        <div key={i} className="source-item">
                          <span>Log Entry {source.index}</span>
                          <span className="score">
  Relevance: {(source.relevance_score ?? 0).toFixed(2)}
</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {streamingMessage && (
          <div className="message assistant">
            <div className="message-content">
              <ReactMarkdown>{streamingMessage}</ReactMarkdown>
              <span className="typing-indicator">▋</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your logs..."
          disabled={loading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={loading || !input.trim()}
          className="send-button"
        >
          {loading ? (
            <Loader2 className="spinner" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </form>
    </div>
  )
}

export default ChatInterface


