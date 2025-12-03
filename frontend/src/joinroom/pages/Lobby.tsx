import { useEffect, useState, useRef } from "react";
import { useSocket } from "../../contexts/SocketContext";
import { useLocation, useNavigate } from "react-router-dom";

interface Jugador {
  nombre: string;
  color: string;
}

const Lobby = () => {
  const { lastMessage, send, connected } = useSocket();
  const location = useLocation();
  const [jugadores, setJugadores] = useState<Jugador[]>([]);
  const [conectados, setConectados] = useState(0);
  const [requeridos, setRequeridos] = useState(2); // Mínimo para iniciar
  const MAX_JUGADORES = 4; // Máximo de jugadores permitidos
  // Si viene de /create-room (sin state o isAdmin true), es admin
  // Si viene de /join-room (isAdmin: false), no es admin
  const [esAdmin, setEsAdmin] = useState(location.state?.isAdmin ?? true);
  const [roomCode] = useState(location.state?.roomCode || "");
  const [mensaje, setMensaje] = useState("");
  // Obtener miInfo del state si viene (para el admin que crea la sala)
  const [miInfo, setMiInfo] = useState<Jugador | null>(() => {
    const state = location.state as any;
    if (state?.playerName && state?.playerColor) {
      return { nombre: state.playerName, color: state.playerColor };
    }
    return null;
  });
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();
  // Flag para saber si se recibió DETERMINACION_INICIO
  const pendingTurnDetermination = useRef(false);

  // Copiar código de sala
  const handleCopy = () => {
    navigator.clipboard.writeText(roomCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    if (!lastMessage) return;
    
    console.log('📩 Lobby recibió mensaje:', lastMessage);
    
    // Mensaje de bienvenida - info del jugador actual
    if (lastMessage.tipo === "BIENVENIDA") {
      const nuevoJugador = {
        nombre: lastMessage.nombre,
        color: lastMessage.color
      };
      setMiInfo(nuevoJugador);
      setJugadores(prev => {
        if (!prev.find(j => j.nombre === nuevoJugador.nombre)) {
          return [...prev, nuevoJugador];
        }
        return prev;
      });
    }
    
    // Mensaje de espera - conteo de jugadores
    if (lastMessage.tipo === "ESPERANDO") {
      setConectados(lastMessage.conectados || 0);
      setRequeridos(lastMessage.requeridos || 2);
      if (Array.isArray(lastMessage.jugadores)) {
        setJugadores(lastMessage.jugadores);
      }
    }
    
    // Mensaje INFO - puede indicar si eres admin
    if (lastMessage.tipo === "INFO") {
      if (lastMessage.es_admin !== undefined) {
        setEsAdmin(lastMessage.es_admin);
      }
      if (lastMessage.mensaje) {
        setMensaje(lastMessage.mensaje);
      }
    }
    
    // Lista de jugadores actualizada
    if (lastMessage.tipo === "LISTA_JUGADORES" && Array.isArray(lastMessage.jugadores)) {
      setJugadores(lastMessage.jugadores);
    }
    
    // Nuevo jugador conectado - agregarlo a la lista
    if (lastMessage.tipo === "JUGADOR_CONECTADO") {
      const nuevoJugador = {
        nombre: lastMessage.nombre,
        color: lastMessage.color
      };
      setJugadores(prev => {
        if (!prev.find(j => j.nombre === nuevoJugador.nombre)) {
          return [...prev, nuevoJugador];
        }
        return prev;
      });
    }
    
    // Jugador desconectado
    if (lastMessage.tipo === "JUGADOR_DESCONECTADO") {
      setJugadores(prev => prev.filter(j => j.nombre !== lastMessage.nombre));
    }

    // Si recibimos DETERMINACION_INICIO, marcamos el flag
    if (lastMessage.tipo === "DETERMINACION_INICIO") {
      console.log('🎲 Recibido DETERMINACION_INICIO, jugador_actual:', lastMessage.jugador_actual);
      console.log('🎲 Estado actual - miInfo:', miInfo, 'jugadores:', jugadores, 'esAdmin:', esAdmin);
      pendingTurnDetermination.current = true;
    }
    
    // Si el flag está activo, navegamos
    if (pendingTurnDetermination.current) {
      // Construir lista de jugadores - usar jugadores si existe, sino crear desde miInfo
      let listaJugadores = jugadores.length > 0 ? jugadores : (miInfo ? [miInfo] : []);
      
      console.log('🔍 pendingTurnDetermination activo, listaJugadores:', listaJugadores);
      
      if (listaJugadores.length === 0) {
        console.log('⏳ Esperando lista de jugadores...');
        return;
      }
      
      // Usar el ID del servidor si está disponible (j.id), sino usar el índice
      const jugadoresTurno = listaJugadores.map((j: any, idx) => ({
        id: j.id !== undefined ? j.id : idx,
        name: j.nombre,
        color: j.color
      }));
      
      console.log('🔍 jugadoresTurno construido:', jugadoresTurno);
      
      // Intentar obtener miId de miInfo
      let miId: number | undefined;
      if (miInfo) {
        miId = jugadoresTurno.find(j => j.name === miInfo.nombre)?.id;
        console.log('🔍 Buscando miId por nombre:', miInfo.nombre, '-> encontrado:', miId);
      }
      
      // Si aún no tenemos miId, buscar por color
      if (miId === undefined && miInfo) {
        miId = jugadoresTurno.find(j => j.color === miInfo.color)?.id;
        console.log('🔍 Buscando miId por color:', miInfo.color, '-> encontrado:', miId);
      }
      
      // Si aún no tenemos miId y somos admin, usamos el primer jugador
      if (miId === undefined && esAdmin && jugadoresTurno.length > 0) {
        miId = 0; // El admin suele ser el primer jugador
        console.log('🔍 Usando miId=0 para admin');
      }
      
      // FALLBACK: Si aún no tenemos miId pero tenemos miInfo, forzar navegación
      if (miId === undefined && miInfo && jugadoresTurno.length > 0) {
        console.log('⚠️ FALLBACK: No se encontró miId, buscando por cualquier coincidencia');
        const miJugador = jugadoresTurno.find((j: any) => 
          j.name === miInfo.nombre || j.color === miInfo.color
        );
        if (miJugador) {
          miId = miJugador.id;
          console.log('🔍 Fallback encontró jugador:', miJugador);
        } else {
          // Último recurso: usar el índice basado en el color
          const colorIndex = jugadoresTurno.findIndex((j: any) => j.color === miInfo.color);
          if (colorIndex >= 0) {
            miId = jugadoresTurno[colorIndex].id;
            console.log('🔍 Fallback por índice de color:', colorIndex, '-> id:', miId);
          }
        }
      }
      
      if (typeof miId === 'number') {
        console.log('🚀 Navegando a determinar-turno con miId:', miId, 'jugadores:', jugadoresTurno);
        pendingTurnDetermination.current = false;
        
        // Construir playerInfo para pasar al juego
        const playerInfo = miInfo ? {
          id: miId,
          nombre: miInfo.nombre,
          color: miInfo.color
        } : null;
        
        navigate('/determinar-turno', { 
          state: { 
            players: jugadoresTurno, 
            myId: miId,
            playerInfo: playerInfo
          } 
        });
      }
    }
  }, [lastMessage, jugadores, miInfo, esAdmin, navigate]);

  // Botón solo visible si eres admin y hay suficientes jugadores (2-4)
  const puedeIniciar = esAdmin && conectados >= requeridos && conectados <= MAX_JUGADORES;

  const handleIniciar = () => {
    send({ tipo: "LISTO" });
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #5b21b6 0%, #9333ea 50%, #ec4899 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        borderRadius: '2rem',
        padding: '2rem',
        color: 'white',
        maxWidth: '500px',
        width: '100%',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        border: '4px solid rgba(255, 255, 255, 0.3)'
      }}>
        <h2 style={{
          fontSize: '2rem',
          fontWeight: '900',
          marginBottom: '1.5rem',
          textAlign: 'center',
          background: 'linear-gradient(90deg, #fef08a, #fbcfe8)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          {esAdmin ? '🎮 Sala de Espera' : '🎮 Lobby'}
        </h2>

        {/* Código de sala (solo admin) */}
        {esAdmin && roomCode && (
          <div style={{
            background: 'rgba(251, 191, 36, 0.2)',
            border: '2px solid rgba(251, 191, 36, 0.5)',
            borderRadius: '1rem',
            padding: '1rem',
            marginBottom: '1rem',
            textAlign: 'center'
          }}>
            <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: 'rgba(255,255,255,0.8)' }}>
              Comparte este código:
            </p>
            <div style={{
              fontSize: '1.5rem',
              fontWeight: '900',
              letterSpacing: '0.1em',
              color: '#fde047',
              marginBottom: '0.5rem'
            }}>
              {roomCode}
            </div>
            <button
              onClick={handleCopy}
              style={{
                background: copied ? '#22c55e' : 'rgba(255,255,255,0.2)',
                border: 'none',
                borderRadius: '0.5rem',
                padding: '0.5rem 1rem',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '600'
              }}
            >
              {copied ? '✅ Copiado!' : '📋 Copiar código'}
            </button>
          </div>
        )}

        {/* Estado de conexión */}
        {!connected && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.2)',
            border: '2px solid rgba(239, 68, 68, 0.5)',
            borderRadius: '0.5rem',
            padding: '0.75rem',
            marginBottom: '1rem',
            textAlign: 'center'
          }}>
            ⚠️ Desconectado del servidor
          </div>
        )}

        {/* Tu información */}
        {miInfo && (
          <div style={{
            background: 'rgba(52, 211, 153, 0.2)',
            border: '2px solid rgba(52, 211, 153, 0.5)',
            borderRadius: '0.5rem',
            padding: '0.75rem',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <div style={{
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: miInfo.color === 'amarillo' ? '#fbbf24' :
                         miInfo.color === 'azul' ? '#3b82f6' :
                         miInfo.color === 'rojo' ? '#ef4444' :
                         miInfo.color === 'verde' ? '#22c55e' : '#9ca3af'
            }} />
            <span>Tú: <strong>{miInfo.nombre}</strong> ({miInfo.color})</span>
            {esAdmin && <span style={{ marginLeft: 'auto', background: '#fbbf24', color: '#1f2937', padding: '0.125rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.75rem', fontWeight: '700' }}>Admin</span>}
          </div>
        )}

        {/* Lista de jugadores */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '1rem',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1rem' }}>
            Jugadores conectados ({conectados}/{MAX_JUGADORES})
          </h3>
          {jugadores.length === 0 && !miInfo ? (
            <div style={{ color: 'rgba(255,255,255,0.7)', fontStyle: 'italic', textAlign: 'center' }}>
              <p>👥 {conectados} jugador{conectados !== 1 ? 'es' : ''} en la sala</p>
              <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                Esperando jugadores...
              </p>
            </div>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {/* Mostrar jugadores de la lista o al menos miInfo */}
              {(jugadores.length > 0 ? jugadores : (miInfo ? [miInfo] : [])).map((j, idx) => (
                <li key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '0.5rem',
                  marginBottom: '0.5rem'
                }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    background: j.color === 'amarillo' ? '#fbbf24' :
                               j.color === 'azul' ? '#3b82f6' :
                               j.color === 'rojo' ? '#ef4444' :
                               j.color === 'verde' ? '#22c55e' : '#9ca3af'
                  }} />
                  <span style={{ fontWeight: '600' }}>
                    {j.nombre || `Jugador ${idx + 1}`}
                  </span>
                  <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.875rem' }}>
                    ({j.color})
                  </span>
                  {idx === 0 && esAdmin && (
                    <span style={{
                      marginLeft: 'auto',
                      background: '#fbbf24',
                      color: '#1f2937',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '0.25rem',
                      fontSize: '0.75rem',
                      fontWeight: '700'
                    }}>Admin</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Vista para ADMIN */}
        {esAdmin && (
          <div>
            {puedeIniciar ? (
              <button
                onClick={handleIniciar}
                style={{
                  width: '100%',
                  background: 'linear-gradient(90deg, #34d399, #10b981)',
                  color: 'white',
                  fontWeight: '900',
                  fontSize: '1.125rem',
                  padding: '1rem 2rem',
                  borderRadius: '1rem',
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: '0 10px 30px rgba(52, 211, 153, 0.5)',
                  transition: 'transform 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
              >
                🚀 Iniciar Partida
              </button>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '1rem',
                background: 'rgba(251, 191, 36, 0.2)',
                borderRadius: '1rem',
                border: '2px solid rgba(251, 191, 36, 0.5)'
              }}>
                <p style={{ fontWeight: '600' }}>
                  ⏳ Se necesitan entre 2 y 4 jugadores para iniciar
                </p>
                <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)', marginTop: '0.5rem' }}>
                  Comparte el código de la sala con tus amigos
                </p>
              </div>
            )}
          </div>
        )}

        {/* Vista para JUGADORES (no admin) */}
        {!esAdmin && (
          <div style={{
            textAlign: 'center',
            padding: '1.5rem',
            background: 'rgba(96, 165, 250, 0.2)',
            borderRadius: '1rem',
            border: '2px solid rgba(96, 165, 250, 0.5)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '0.5rem',
              marginBottom: '1rem'
            }}>
              <div style={{ width: '10px', height: '10px', background: '#60a5fa', borderRadius: '50%', animation: 'pulse 1.5s infinite' }} />
              <div style={{ width: '10px', height: '10px', background: '#60a5fa', borderRadius: '50%', animation: 'pulse 1.5s infinite 0.2s' }} />
              <div style={{ width: '10px', height: '10px', background: '#60a5fa', borderRadius: '50%', animation: 'pulse 1.5s infinite 0.4s' }} />
            </div>
            <p style={{ fontWeight: '700', fontSize: '1.125rem' }}>
              ⏳ Esperando que el anfitrión inicie la partida...
            </p>
            <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)', marginTop: '0.5rem' }}>
              La partida comenzará pronto
            </p>
          </div>
        )}

        {mensaje && (
          <p style={{
            marginTop: '1rem',
            padding: '0.75rem',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '0.5rem',
            textAlign: 'center'
          }}>
            {mensaje}
          </p>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.8); }
        }
      `}</style>
    </div>
  );
};

export default Lobby;
