import React from 'react';
import type { ColorJugador, FichaEstado } from '../types/gameTypes';

// Colores más oscuros y visibles para las fichas
const COLORES_FICHA: Record<ColorJugador, { bg: string; borde: string; texto: string }> = {
  rojo: { bg: '#C41E3A', borde: '#8B0000', texto: '#FFD700' },
  azul: { bg: '#0047AB', borde: '#00008B', texto: '#FFFFFF' },
  verde: { bg: '#228B22', borde: '#006400', texto: '#FFFFFF' },
  amarillo: { bg: '#DAA520', borde: '#B8860B', texto: '#000000' }
};

interface FichaProps {
  id: number;
  color: ColorJugador;
  estado: FichaEstado;
  seleccionada?: boolean;
  seleccionable?: boolean;
  onClick?: (event: React.MouseEvent) => void;
  size?: 'small' | 'medium' | 'large';
}

const Ficha: React.FC<FichaProps> = ({
  id,
  color,
  estado,
  seleccionada = false,
  seleccionable = false,
  onClick,
  size = 'medium'
}) => {
  const colores = COLORES_FICHA[color];
  
  // Tamaños compactos para caber en casillas de 40px
  const sizes = {
    small: { outer: 14, inner: 10, text: 7 },
    medium: { outer: 20, inner: 14, text: 9 },
    large: { outer: 28, inner: 20, text: 11 }
  };
  
  const s = sizes[size];
  
  // Estilo base de la ficha
  const baseStyle: React.CSSProperties = {
    width: s.outer,
    height: s.outer,
    borderRadius: '50%',
    backgroundColor: colores.bg,
    // ENTORNO NEGRO para fichas seleccionables
    border: seleccionable ? '3px solid #000000' : `2px solid ${colores.borde}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: seleccionable ? 'pointer' : 'default',
    transition: 'all 0.2s ease',
    boxShadow: seleccionada 
      ? `0 0 0 2px white, 0 0 0 4px ${colores.bg}, 0 4px 8px rgba(0,0,0,0.4)`
      : seleccionable 
        ? '0 4px 8px rgba(0,0,0,0.6)'
        : '0 1px 3px rgba(0,0,0,0.3)',
    transform: seleccionada ? 'scale(1.15)' : seleccionable ? 'scale(1.05)' : 'scale(1)',
    position: 'relative',
  };
  
  // Estilo para ficha bloqueada (cárcel) - NO atenuar para que se vea
  if (estado === 'BLOQUEADO') {
    // Sin cambios visuales, se ven igual
  }
  
  // Estilo para ficha en meta
  if (estado === 'META') {
    baseStyle.boxShadow = `0 0 8px 2px gold, ${baseStyle.boxShadow}`;
  }
  
  // Animación pulsante para fichas seleccionables
  const pulseAnimation = seleccionable && !seleccionada ? {
    animation: 'pulse 1.5s infinite'
  } : {};
  
  return (
    <div
      style={{ ...baseStyle, ...pulseAnimation }}
      onClick={(e) => {
        console.log(`🎯 Ficha onClick: id=${id}, color=${color}, seleccionable=${seleccionable}`);
        if (onClick) onClick(e);
      }}
      className={seleccionable ? 'hover:scale-110' : ''}
      title={`Ficha ${id + 1} - ${color} - ${estado}`}
    >
      {/* Círculo interno con número */}
      <div style={{
        width: s.inner,
        height: s.inner,
        borderRadius: '50%',
        backgroundColor: 'rgba(255,255,255,0.3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        fontSize: s.text,
        color: colores.texto,
        textShadow: '0 1px 2px rgba(0,0,0,0.5)'
      }}>
        {id + 1}
      </div>
    </div>
  );
};

// Componente para agrupar fichas en una casilla
interface GrupoFichasProps {
  fichas: Array<{
    id: number;
    color: ColorJugador;
    estado: FichaEstado;
  }>;
  fichaSeleccionada?: { color: ColorJugador; id: number } | null;
  fichasSeleccionables?: Array<{ color: ColorJugador; id: number }>;
  onFichaClick?: (color: ColorJugador, id: number, event?: React.MouseEvent) => void;
}

export const GrupoFichas: React.FC<GrupoFichasProps> = ({
  fichas,
  fichaSeleccionada,
  fichasSeleccionables = [],
  onFichaClick
}) => {
  if (fichas.length === 0) return null;
  
  // Posiciones compactas para hasta 4 fichas en una casilla de 40px
  const positions = [
    { top: 3, left: 3 },
    { top: 3, left: 17 },
    { top: 17, left: 3 },
    { top: 17, left: 17 }
  ];
  
  return (
    <div style={{ 
      position: 'relative', 
      width: 32, 
      height: 32,
      display: 'flex',
      flexWrap: 'wrap',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {fichas.map((ficha, idx) => {
        const esSeleccionable = fichasSeleccionables.some(
          f => f.color === ficha.color && f.id === ficha.id
        );
        const esSeleccionada = fichaSeleccionada?.color === ficha.color && 
                               fichaSeleccionada?.id === ficha.id;
        
        console.log(`🔍 GrupoFichas: ficha ${ficha.color}-${ficha.id}, seleccionable=${esSeleccionable}, fichasSeleccionables=`, fichasSeleccionables);
        
        return (
          <div 
            key={`${ficha.color}-${ficha.id}`}
            style={{
              position: fichas.length > 1 ? 'absolute' : 'relative',
              ...(fichas.length > 1 ? positions[idx % 4] : {}),
              zIndex: esSeleccionada ? 10 : idx,
              pointerEvents: 'auto' // Asegurar que los eventos del mouse funcionen
            }}
            onClick={(e) => {
              console.log(`🎯 Wrapper onClick: ${ficha.color}-${ficha.id}`);
              e.stopPropagation();
              onFichaClick?.(ficha.color, ficha.id, e);
            }}
          >
            <Ficha
              id={ficha.id}
              color={ficha.color}
              estado={ficha.estado}
              seleccionada={esSeleccionada}
              seleccionable={esSeleccionable}
              onClick={(e) => {
                console.log(`🎯 Ficha onClick interno: ${ficha.color}-${ficha.id}`);
                onFichaClick?.(ficha.color, ficha.id, e);
              }}
              size="small"
            />
          </div>
        );
      })}
    </div>
  );
};

// CSS para animación de pulso
const pulseKeyframes = `
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(147, 51, 234, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 8px rgba(147, 51, 234, 0);
  }
}
`;

// Inyectar estilos de animación
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = pulseKeyframes;
  document.head.appendChild(style);
}

export default Ficha;
