import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Send, Bot, User, Sparkles, Mic, Square, Target, BarChart, School, FileText, Paperclip, Lock, ArrowRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { sendChatMessage, sendAudioMessage, uploadTranscript } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const FREE_MESSAGE_LIMIT = 3;

const ChatInterface = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      isWelcome: true,
      sender: 'bot',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [guestMsgCount, setGuestMsgCount] = useState(0);
  const [showAuthGate, setShowAuthGate] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    inputRef.current?.focus();
    
    // Check for transcript context from Router state
    if (location.state && location.state.transcriptContext) {
      const data = location.state.transcriptContext;
      
      // Clear the state so it doesn't trigger again on refresh
      navigate('.', { replace: true, state: {} });
      
      try {
        const notesStr = data.notes ? Object.entries(data.notes).map(([k,v]) => `${k}: ${v}/20`).join(', ') : 'Aucune note extraite';
        
        const autoMsgText = `Voici mon profil académique basé sur mon relevé de notes :\n- Série : ${data.serie || 'Non précisée'}\n- Mention : ${data.mention || 'Non précisée'}\n- Notes : ${notesStr}\n\nQuelles filières me recommandes-tu ?`;
        
        const userMsg = { id: Date.now(), isTranscript: true, text: autoMsgText, sender: 'user' };
        setMessages((prev) => [...prev, userMsg]);
        setIsLoading(true);
        
        // Send it to the backend immediately
        sendChatMessage(autoMsgText, sessionId).then((res) => {
          processResponse(res);
          setIsLoading(false);
        }).catch(err => {
          handleError(err);
          setIsLoading(false);
        });
      } catch(e) {
        console.error("Erreur parsing transcript", e);
      }
    } else if (location.state && location.state.initialQuery) {
      const query = location.state.initialQuery;
      // Clear the state
      navigate('.', { replace: true, state: {} });
      
      const userMsg = { id: Date.now(), text: query, sender: 'user' };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      
      sendChatMessage(query, sessionId).then((res) => {
        processResponse(res);
        setIsLoading(false);
      }).catch(err => {
        handleError(err);
        setIsLoading(false);
      });
    } else {
      // Fallback: check localStorage just in case
      const transcriptCtx = localStorage.getItem('transcriptContext');
      if (transcriptCtx) {
        localStorage.removeItem('transcriptContext');
        try {
          const data = JSON.parse(transcriptCtx);
          const notesStr = data.notes ? Object.entries(data.notes).map(([k,v]) => `${k}: ${v}/20`).join(', ') : 'Aucune note extraite';
          
          const autoMsgText = `Voici mon profil académique basé sur mon relevé de notes :\n- Série : ${data.serie || 'Non précisée'}\n- Mention : ${data.mention || 'Non précisée'}\n- Notes : ${notesStr}\n\nQuelles filières me recommandes-tu ?`;
          
          const userMsg = { id: Date.now(), isTranscript: true, text: autoMsgText, sender: 'user' };
          setMessages((prev) => [...prev, userMsg]);
          setIsLoading(true);
          
          sendChatMessage(autoMsgText, sessionId).then((res) => {
            processResponse(res);
            setIsLoading(false);
          }).catch(err => {
            handleError(err);
            setIsLoading(false);
          });
        } catch(e) {
          console.error("Erreur parsing transcript", e);
        }
      }
    }
  }, [location.state, navigate, sessionId]);

  const checkGuestLimit = () => {
    if (!isAuthenticated && guestMsgCount >= FREE_MESSAGE_LIMIT) {
      setShowAuthGate(true);
      return false;
    }
    return true;
  };

  const handleSend = async (e) => {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed || isLoading || isRecording) return;
    if (!checkGuestLimit()) return;

    const userMsg = { id: Date.now(), text: trimmed, sender: 'user' };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);
    if (!isAuthenticated) setGuestMsgCount(prev => prev + 1);

    try {
      const data = await sendChatMessage(trimmed, sessionId);
      processResponse(data);
    } catch (err) {
      handleError(err);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setIsLoading(true);
        
        // Show a temporary user message for audio
        const userMsg = { id: Date.now(), text: "🎤 Message vocal envoyé...", sender: 'user' };
        setMessages((prev) => [...prev, userMsg]);

        try {
          const data = await sendAudioMessage(audioBlob, sessionId);
          
          // Update the user message with actual transcription if available
          if (data.transcription) {
            setMessages((prev) => 
              prev.map(msg => msg.id === userMsg.id ? { ...msg, text: `🎤 "${data.transcription}"` } : msg)
            );
          }
          
          processResponse(data);
        } catch (err) {
          handleError(err);
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Impossible d'accéder au microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
      const errorMsg = { id: Date.now(), text: "⚠️ Veuillez uploader un fichier PDF uniquement.", sender: 'bot' };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await uploadTranscript(file);
      const data = response.data;
      
      const notesStr = data.notes ? Object.entries(data.notes).map(([k,v]) => `${k}: ${v}/20`).join(', ') : 'Aucune note extraite';
      const autoMsgText = `J'ai importé mon relevé de notes :\n- Série : ${data.serie || 'Non précisée'}\n- Mention : ${data.mention || 'Non précisée'}\n- Notes : ${notesStr}\n\nQuelles filières me recommandes-tu ?`;
      
      const userMsg = { id: Date.now(), isTranscript: true, text: autoMsgText, sender: 'user' };
      setMessages((prev) => [...prev, userMsg]);
      
      const res = await sendChatMessage(autoMsgText, sessionId);
      processResponse(res);
    } catch (err) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail || "Erreur lors de l'analyse du document.";
      const errorMsg = { id: Date.now(), text: `⚠️ ${errorMessage}`, sender: 'bot' };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
      inputRef.current?.focus();
    }
  };

  const processResponse = (data) => {
    if (data.session_id && !sessionId) {
      setSessionId(data.session_id);
    }
    const botMsg = {
      id: Date.now() + 1,
      text: data.response || "Désolé, je n'ai pas pu traiter votre message.",
      sender: 'bot',
    };
    setMessages((prev) => [...prev, botMsg]);
  };

  const handleError = (err) => {
    console.error('Chat error:', err);
    const errorMsg = {
      id: Date.now() + 1,
      text: "⚠️ Désolé, une erreur est survenue. Vérifiez que le serveur backend est lancé et réessayez.",
      sender: 'bot',
    };
    setMessages((prev) => [...prev, errorMsg]);
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-avatar">
          <Bot size={24} color="white" />
        </div>
        <div className="chat-header-info">
          <h2>
            EduBot Assistant
            <span className="chat-status-dot" />
          </h2>
          <p>IA d'orientation intelligente</p>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.sender}`}>
            <div className={`chat-message-avatar ${msg.sender}`}>
              {msg.sender === 'bot' ? (
                <Sparkles size={18} color="white" />
              ) : (
                <User size={18} />
              )}
            </div>
            <div className="chat-message-bubble">
              {msg.isWelcome ? (
                <div className="chat-markdown">
                  <p><strong>Bonjour !</strong> Je suis <strong>EduBot</strong>, votre conseiller d'orientation académique en Guinée.</p>
                  <p>Afin de vous guider avec précision, je m'appuie sur des données réelles du Ministère de l'Enseignement Supérieur. Je peux vous accompagner pour :</p>
                  <ul style={{ listStyle: 'none', padding: 0, margin: '1rem 0' }}>
                    <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}><Target size={16} color="var(--accent-1)" /> Trouver la filière idéale selon votre profil</li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}><BarChart size={16} color="var(--accent-1)" /> Analyser vos notes pour évaluer vos chances</li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><School size={16} color="var(--accent-1)" /> Découvrir les universités guinéennes et leurs débouchés</li>
                  </ul>
                  <p><em>Pour commencer, pourriez-vous m'indiquer votre série du baccalauréat et vos meilleures matières ?</em></p>
                </div>
              ) : msg.isTranscript ? (
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <FileText size={20} color="var(--accent-2)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--accent-2)', marginBottom: '0.25rem' }}>Relevé de notes transmis</div>
                    <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>{msg.text.split('\n\n')[0]}</div>
                    <div style={{ marginTop: '0.5rem', fontWeight: 500 }}>Quelles filières me recommandes-tu ?</div>
                  </div>
                </div>
              ) : msg.sender === 'bot' ? (
                <div className="chat-markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.text}
                  </ReactMarkdown>
                </div>
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-message bot">
            <div className="chat-message-avatar bot">
              <Sparkles size={18} color="white" />
            </div>
            <div className="chat-message-bubble">
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <form onSubmit={handleSend} className="chat-input-form">
          <input
            type="file"
            accept=".pdf"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <button
            type="button"
            className="chat-send-btn"
            style={{ 
              background: 'transparent',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              marginRight: '0.5rem'
            }}
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isRecording}
            aria-label="Importer un relevé de notes"
            title="Importer un relevé de notes (PDF)"
          >
            <Paperclip size={20} />
          </button>
          
          <button
            type="button"
            className="chat-send-btn"
            style={{ 
              background: isRecording ? 'rgba(253, 121, 168, 0.2)' : 'var(--bg-primary)',
              color: isRecording ? 'var(--accent-3)' : 'var(--text-secondary)',
              border: `1px solid ${isRecording ? 'var(--accent-3)' : 'var(--border-subtle)'}`
            }}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading}
            aria-label="Enregistrer un message vocal"
          >
            {isRecording ? <Square size={20} /> : <Mic size={20} />}
          </button>
          
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={isRecording ? "Enregistrement en cours..." : "Posez votre question d'orientation..."}
            disabled={isLoading || isRecording}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={(!inputValue.trim() && !isRecording) || isLoading}
            aria-label="Envoyer"
          >
            <Send size={20} color="white" />
          </button>
        </form>
      </div>
      {/* Auth Gate Modal */}
      {showAuthGate && (
        <div className="auth-gate-overlay" onClick={() => setShowAuthGate(false)}>
          <div className="auth-gate-modal" onClick={(e) => e.stopPropagation()}>
            <div className="auth-gate-icon">
              <Lock size={28} color="var(--accent-1)" />
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              Créez votre compte gratuit
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              Vous avez utilisé vos <strong>{FREE_MESSAGE_LIMIT} messages gratuits</strong>. 
              Inscrivez-vous pour continuer à discuter avec EduBot sans limite et sauvegarder vos recommandations.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <Link to="/auth" className="btn btn-primary" style={{ flex: 1, textAlign: 'center' }}>
                S'inscrire <ArrowRight size={16} />
              </Link>
              <button 
                className="btn btn-secondary" 
                style={{ flex: 1 }}
                onClick={() => setShowAuthGate(false)}
              >
                Plus tard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
