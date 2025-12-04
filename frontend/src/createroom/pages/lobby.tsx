import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateRoom } from '../hooks/useCreateRoom';
import { ColorSelector } from '../components/ColorSelector';
import { obtenerSesion } from '../../auth/services/authService';

export const CreateRoom: React.FC = () => {
  const navigate = useNavigate();
  const { create, roomCode, loading, error, connected } = useCreateRoom();
  const [name, setName] = useState('');
  const [color, setColor] = useState('');
  const [copied, setCopied] = useState(false);

  // Cargar el nombre del usuario si está logueado
  useEffect(() => {
    const sesion = obtenerSesion();
    if (sesion) {
      setName(sesion.username);
    }
  }, []);

  const handleCreate = async () => {
    if (!name.trim() || !color) return;
    await create(name.trim(), color);
  };

  // Navegar al lobby cuando la conexión esté establecida
  const handleGoToLobby = () => {
    if (roomCode && connected) {
      navigate('/lobby', { state: { isAdmin: true, roomCode, playerName: name.trim(), playerColor: color } });
    }
  };

  const handleCopy = () => {
    // Método alternativo que funciona en HTTP (no solo HTTPS)
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(roomCode);
    } else {
      // Fallback para HTTP
      const textArea = document.createElement('textarea');
      textArea.value = roomCode;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (roomCode) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #5b21b6 0%, #9333ea 50%, #ec4899 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'clamp(0.5rem, 2vw, 1rem)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Círculos decorativos */}
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          width: 'clamp(80px, 15vw, 128px)',
          height: 'clamp(80px, 15vw, 128px)',
          background: 'rgba(251, 191, 36, 0.2)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          animation: 'pulse 2s infinite'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '40px',
          right: '40px',
          width: 'clamp(100px, 18vw, 160px)',
          height: 'clamp(100px, 18vw, 160px)',
          background: 'rgba(96, 165, 250, 0.2)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          animation: 'pulse 2s infinite'
        }} />

        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          borderRadius: 'clamp(1.5rem, 4vw, 2.5rem)',
          padding: 'clamp(1.5rem, 4vw, 3rem)',
          textAlign: 'center',
          color: 'white',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          border: '3px solid rgba(255, 255, 255, 0.3)',
          position: 'relative',
          zIndex: 10
        }}>
          <div style={{
            marginBottom: 'clamp(1rem, 3vw, 2rem)',
            display: 'flex',
            justifyContent: 'center'
          }}>
            <div style={{
              background: 'linear-gradient(135deg, #34d399, #10b981)',
              borderRadius: '50%',
              padding: 'clamp(0.75rem, 2vw, 1rem)',
              boxShadow: '0 10px 30px rgba(52, 211, 153, 0.5)',
              animation: 'bounce 1s infinite'
            }}>
              <svg style={{ width: 'clamp(40px, 10vw, 64px)', height: 'clamp(40px, 10vw, 64px)' }} fill="none" stroke="white" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          <h2 style={{
            fontSize: 'clamp(1.75rem, 6vw, 3rem)',
            fontWeight: '900',
            marginBottom: 'clamp(0.5rem, 2vw, 1rem)',
            background: 'linear-gradient(90deg, #fef08a, #fbcfe8)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))'
          }}>
            ¡Sala Creada!
          </h2>

          <p style={{
            fontSize: 'clamp(1rem, 3vw, 1.25rem)',
            marginBottom: 'clamp(1rem, 2vw, 1.5rem)',
            fontWeight: '600',
            color: 'rgba(255, 255, 255, 0.9)'
          }}>
            Comparte este código con tus amigos:
          </p>

          <div style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1))',
            backdropFilter: 'blur(10px)',
            borderRadius: 'clamp(1rem, 3vw, 2rem)',
            padding: 'clamp(1rem, 3vw, 2rem)',
            marginBottom: 'clamp(1rem, 2vw, 1.5rem)',
            border: '3px solid rgba(255, 255, 255, 0.4)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
            transition: 'transform 0.3s',
            cursor: 'pointer',
            overflow: 'hidden'
          }}>
            <div style={{
              fontSize: 'clamp(1.75rem, 8vw, 4rem)',
              fontWeight: '900',
              letterSpacing: 'clamp(0.05em, 1vw, 0.1em)',
              color: '#fde047',
              textShadow: '0 0 30px rgba(253, 224, 71, 0.5)',
              animation: 'pulse 2s infinite',
              wordBreak: 'break-all'
            }}>
              {roomCode}
            </div>
          </div>

          <button
            onClick={handleCopy}
            style={{
              width: '100%',
              background: 'linear-gradient(90deg, #fbbf24, #fb923c)',
              color: '#1f2937',
              fontWeight: '900',
              fontSize: 'clamp(0.9rem, 3vw, 1.125rem)',
              padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1rem, 3vw, 2rem)',
              borderRadius: 'clamp(1rem, 3vw, 2rem)',
              border: '3px solid #fcd34d',
              cursor: 'pointer',
              transition: 'transform 0.3s',
              boxShadow: '0 10px 30px rgba(251, 191, 36, 0.5)',
              marginBottom: 'clamp(0.75rem, 2vw, 1rem)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
            onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
            onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          >
            {copied ? (
              <>
                <svg style={{ width: '24px', height: '24px' }} fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                ¡Copiado!
              </>
            ) : (
              <>
                <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copiar código
              </>
            )}
          </button>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            color: 'rgba(255, 255, 255, 0.8)'
          }}>
            <div style={{ display: 'flex', gap: '0.25rem' }}>
              <div style={{
                width: '8px',
                height: '8px',
                background: '#34d399',
                borderRadius: '50%',
                animation: 'pulse 1.5s infinite'
              }} />
              <div style={{
                width: '8px',
                height: '8px',
                background: '#34d399',
                borderRadius: '50%',
                animation: 'pulse 1.5s infinite 0.15s'
              }} />
              <div style={{
                width: '8px',
                height: '8px',
                background: '#34d399',
                borderRadius: '50%',
                animation: 'pulse 1.5s infinite 0.3s'
              }} />
            </div>
            <p style={{ fontSize: '1.125rem', fontWeight: '600' }}>
              Esperando jugadores...
            </p>
          </div>

          {/* Botón para ir al Lobby */}
          <button
            onClick={handleGoToLobby}
            disabled={!connected}
            style={{
              width: '100%',
              marginTop: 'clamp(1rem, 2vw, 1.5rem)',
              background: connected 
                ? 'linear-gradient(90deg, #34d399, #10b981)' 
                : 'rgba(156, 163, 175, 0.5)',
              color: 'white',
              fontWeight: '900',
              fontSize: 'clamp(0.9rem, 3vw, 1.125rem)',
              padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1rem, 3vw, 2rem)',
              borderRadius: 'clamp(1rem, 3vw, 2rem)',
              border: connected ? '3px solid #6ee7b7' : '3px solid rgba(156, 163, 175, 0.3)',
              cursor: connected ? 'pointer' : 'not-allowed',
              transition: 'transform 0.3s',
              boxShadow: connected ? '0 10px 30px rgba(52, 211, 153, 0.5)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => connected && (e.currentTarget.style.transform = 'scale(1.05)')}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <svg style={{ width: '24px', height: '24px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
            {connected ? 'Ir al Lobby' : 'Conectando...'}
          </button>
        </div>

        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
          @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #5b21b6 0%, #9333ea 50%, #ec4899 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 'clamp(0.5rem, 2vw, 1rem)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Círculos decorativos */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        width: 'clamp(80px, 15vw, 128px)',
        height: 'clamp(80px, 15vw, 128px)',
        background: 'rgba(251, 191, 36, 0.2)',
        borderRadius: '50%',
        filter: 'blur(60px)',
        animation: 'pulse 2s infinite'
      }} />
      <div style={{
        position: 'absolute',
        bottom: '40px',
        right: '40px',
        width: 'clamp(100px, 18vw, 160px)',
        height: 'clamp(100px, 18vw, 160px)',
        background: 'rgba(96, 165, 250, 0.2)',
        borderRadius: '50%',
        filter: 'blur(60px)',
        animation: 'pulse 2s infinite'
      }} />

      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        borderRadius: 'clamp(1.5rem, 4vw, 2.5rem)',
        padding: 'clamp(1.5rem, 4vw, 3rem)',
        textAlign: 'center',
        color: 'white',
        maxWidth: '600px',
        width: '100%',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        border: '3px solid rgba(255, 255, 255, 0.3)',
        position: 'relative',
        zIndex: 10
      }}>
        <h2 style={{
          fontSize: 'clamp(1.5rem, 5vw, 3.5rem)',
          fontWeight: '900',
          marginBottom: 'clamp(1rem, 3vw, 2rem)',
          background: 'linear-gradient(90deg, #fef08a, #fbcfe8, #ddd6fe)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))',
          animation: 'pulse 3s infinite'
        }}>
          Crear Sala
        </h2>

        <div style={{ marginBottom: 'clamp(1rem, 2vw, 1.5rem)' }}>
          <label style={{
            display: 'block',
            textAlign: 'left',
            fontSize: 'clamp(0.9rem, 2.5vw, 1.125rem)',
            fontWeight: '700',
            marginBottom: '0.5rem',
            color: 'rgba(255, 255, 255, 0.9)',
            textShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            ¿Cómo te llamas?
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Escribe tu nombre aquí..."
            maxLength={20}
            style={{
              width: '100%',
              padding: 'clamp(0.75rem, 2vw, 1rem) clamp(1rem, 2vw, 1.5rem)',
              borderRadius: 'clamp(1rem, 3vw, 2rem)',
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              fontSize: 'clamp(0.9rem, 2.5vw, 1.125rem)',
              border: '3px solid rgba(255, 255, 255, 0.4)',
              outline: 'none',
              backdropFilter: 'blur(10px)',
              fontWeight: '600',
              boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
              transition: 'all 0.3s',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#fbbf24';
              e.target.style.boxShadow = '0 0 0 4px rgba(251, 191, 36, 0.4)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.4)';
              e.target.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';
            }}
          />
        </div>

        <div style={{ marginBottom: 'clamp(1rem, 2vw, 1.5rem)' }}>
          <label style={{
            display: 'block',
            textAlign: 'left',
            fontSize: 'clamp(0.9rem, 2.5vw, 1.125rem)',
            fontWeight: '700',
            marginBottom: 'clamp(0.5rem, 1.5vw, 0.75rem)',
            color: 'rgba(255, 255, 255, 0.9)',
            textShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            Elige tu color:
          </label>
          <ColorSelector onSelect={setColor} selected={color} />
        </div>

        {error && (
          <div style={{
            marginBottom: 'clamp(1rem, 2vw, 1.5rem)',
            background: 'rgba(239, 68, 68, 0.3)',
            backdropFilter: 'blur(10px)',
            border: '3px solid rgba(248, 113, 113, 0.5)',
            borderRadius: 'clamp(1rem, 3vw, 2rem)',
            padding: 'clamp(0.75rem, 2vw, 1rem)'
          }}>
            <p style={{
              color: '#fee',
              fontSize: 'clamp(0.85rem, 2vw, 1rem)',
              fontWeight: '700',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              margin: 0
            }}>
              <svg style={{ width: '24px', height: '24px' }} fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error}
            </p>
          </div>
        )}

        <button
          onClick={handleCreate}
          disabled={loading || !name.trim() || !color}
          style={{
            width: '100%',
            background: loading || !name.trim() || !color 
              ? 'rgba(156, 163, 175, 0.5)'
              : 'linear-gradient(90deg, #fbbf24, #fb923c)',
            color: '#1f2937',
            fontWeight: '900',
            fontSize: 'clamp(1rem, 3vw, 1.25rem)',
            padding: 'clamp(0.875rem, 2vw, 1.25rem) clamp(1rem, 3vw, 2rem)',
            borderRadius: 'clamp(1rem, 3vw, 2rem)',
            border: '3px solid',
            borderColor: loading || !name.trim() || !color ? 'rgba(156, 163, 175, 0.3)' : '#fcd34d',
            cursor: loading || !name.trim() || !color ? 'not-allowed' : 'pointer',
            transition: 'transform 0.3s',
            boxShadow: loading || !name.trim() || !color 
              ? 'none'
              : '0 10px 30px rgba(251, 191, 36, 0.5)',
            opacity: loading || !name.trim() || !color ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem'
          }}
          onMouseEnter={(e) => {
            if (!loading && name.trim() && color) {
              e.currentTarget.style.transform = 'scale(1.05)';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
          onMouseDown={(e) => {
            if (!loading && name.trim() && color) {
              e.currentTarget.style.transform = 'scale(0.95)';
            }
          }}
          onMouseUp={(e) => {
            if (!loading && name.trim() && color) {
              e.currentTarget.style.transform = 'scale(1.05)';
            }
          }}
        >
          {loading ? (
            <>
              <svg style={{ 
                width: '24px', 
                height: '24px',
                animation: 'spin 1s linear infinite'
              }} viewBox="0 0 24 24">
                <circle style={{ opacity: 0.25 }} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path style={{ opacity: 0.75 }} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Creando sala...
            </>
          ) : (
            <>
              <svg style={{ width: '28px', height: '28px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
              </svg>
              Crear Sala
            </>
          )}
        </button>

        <p style={{
          marginTop: 'clamp(1rem, 2vw, 1.5rem)',
          fontSize: 'clamp(0.75rem, 2vw, 0.875rem)',
          color: 'rgba(255, 255, 255, 0.7)',
          fontWeight: '500'
        }}>
          ✨ Completa tu nombre y elige un color para comenzar
        </p>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        input::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }
      `}</style>
    </div>
  );
};