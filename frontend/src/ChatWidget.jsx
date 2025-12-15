import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import styled from 'styled-components';

// Styled Components
const ChatWidgetContainer = styled.div`
  position: fixed;
  bottom: ${props => props.minimized ? '-500px' : '20px'};
  right: 20px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  transition: bottom 0.3s ease-in-out;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;

  @media (max-width: 480px) {
    width: calc(100vw - 40px);
    height: calc(100vh - 40px);
    bottom: ${props => props.minimized ? '-100vh' : '20px'};
  }
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 16px 16px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const HeaderTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }

  .status-indicator {
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const HeaderControls = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const LanguageSelect = styled.select`
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  outline: none;

  option {
    color: #333;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const IconButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 20px;
  padding: 4px;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.1);
  }
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 12px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
`;

const Message = styled.div`
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  animation: slideIn 0.3s ease-out;

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const MessageBubble = styled.div`
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  background: ${props => props.isUser ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white'};
  color: ${props => props.isUser ? 'white' : '#333'};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
  position: relative;

  .message-time {
    font-size: 10px;
    opacity: 0.7;
    margin-top: 4px;
    display: block;
  }

  .copy-button {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(0, 0, 0, 0.1);
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 11px;
    color: ${props => props.isUser ? 'white' : '#666'};
    opacity: 0;
    transition: opacity 0.2s;
  }

  &:hover .copy-button {
    opacity: 1;
  }
`;

const TypingIndicator = styled.div`
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 16px;
  width: fit-content;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  span {
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
    animation: typing 1.4s infinite;
  }

  span:nth-child(2) {
    animation-delay: 0.2s;
  }

  span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
    }
    30% {
      transform: translateY(-10px);
    }
  }
`;

const ChatInputContainer = styled.div`
  padding: 16px 20px;
  background: white;
  border-radius: 0 0 16px 16px;
  border-top: 1px solid #e5e7eb;
`;

const ChatInputWrapper = styled.div`
  display: flex;
  gap: 10px;
  align-items: flex-end;
`;

const ChatInput = styled.textarea`
  flex: 1;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  resize: none;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
  max-height: 100px;
  min-height: 42px;

  &:focus {
    border-color: #667eea;
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const SendButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 42px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const FloatingButton = styled.button`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  transition: transform 0.2s;
  z-index: 999;

  &:hover {
    transform: scale(1.1);
  }
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 20px;
  color: #666;

  h4 {
    color: #667eea;
    margin-bottom: 10px;
  }

  p {
    font-size: 14px;
    line-height: 1.5;
  }

  .example-questions {
    margin-top: 15px;
    text-align: left;
    background: white;
    padding: 12px;
    border-radius: 8px;
    font-size: 13px;

    h5 {
      margin: 0 0 8px 0;
      color: #667eea;
    }

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        margin: 4px 0;
        color: #666;
        cursor: pointer;

        &:hover {
          color: #667eea;
        }
      }
    }
  }
`;

// Language options
const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'zh', name: '中文' },
  { code: 'hi', name: 'हिन्दी' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' },
  { code: 'ja', name: '日本語' },
  { code: 'ko', name: '한국어' },
  { code: 'pt', name: 'Português' },
  { code: 'ru', name: 'Русский' }
];

const ChatWidget = ({ apiEndpoint = 'http://localhost:5000/api/chat' }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('en');
  const [isLoading, setIsLoading] = useState(false);
  const [minimized, setMinimized] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(apiEndpoint, {
        message: userMessage.content,
        language: language
      });

      const botMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const exampleQuestions = [
    "How do I stake Ethereum?",
    "What's the best hardware wallet?",
    "How do I bridge tokens to Polygon?"
  ];

  return (
    <>
      {minimized && (
        <FloatingButton onClick={() => setMinimized(false)}>
          💬
        </FloatingButton>
      )}

      <ChatWidgetContainer minimized={minimized}>
        <ChatHeader>
          <HeaderTitle>
            <div className="status-indicator" />
            <h3>Crypto Assistant</h3>
          </HeaderTitle>
          <HeaderControls>
            <LanguageSelect
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {LANGUAGES.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </LanguageSelect>
            <IconButton onClick={() => setMinimized(true)}>
              ✕
            </IconButton>
          </HeaderControls>
        </ChatHeader>

        <ChatMessages>
          {messages.length === 0 && (
            <WelcomeMessage>
              <h4>👋 Welcome to Crypto Assistant!</h4>
              <p>I'm here to help you with crypto onboarding, staking, bridging, wallets, and more.</p>
              <div className="example-questions">
                <h5>Try asking:</h5>
                <ul>
                  {exampleQuestions.map((q, idx) => (
                    <li key={idx} onClick={() => setInput(q)}>
                      {q}
                    </li>
                  ))}
                </ul>
              </div>
            </WelcomeMessage>
          )}

          {messages.map((msg, idx) => (
            <Message key={idx} isUser={msg.role === 'user'}>
              <MessageBubble isUser={msg.role === 'user'}>
                {msg.content}
                <span className="message-time">{msg.timestamp}</span>
                {msg.role === 'assistant' && (
                  <button
                    className="copy-button"
                    onClick={() => copyToClipboard(msg.content)}
                  >
                    Copy
                  </button>
                )}
              </MessageBubble>
            </Message>
          ))}

          {isLoading && (
            <TypingIndicator>
              <span></span>
              <span></span>
              <span></span>
            </TypingIndicator>
          )}

          <div ref={messagesEndRef} />
        </ChatMessages>

        <ChatInputContainer>
          <ChatInputWrapper>
            <ChatInput
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about staking, bridging, wallets..."
              rows={1}
              disabled={isLoading}
            />
            <SendButton onClick={sendMessage} disabled={!input.trim() || isLoading}>
              {isLoading ? '...' : 'Send'}
            </SendButton>
          </ChatInputWrapper>
        </ChatInputContainer>
      </ChatWidgetContainer>
    </>
  );
};

export default ChatWidget;
