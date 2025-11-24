import React from 'react';
import CenterImg from '../assets/Finish.jpeg';
import BlueJeil from '../assets/BlueJeil.jpeg';
import GreenJeil from '../assets/GreenJeil.jpeg';
import RedJeil from '../assets/RedJeil.jpeg';
import YellowJeil from '../assets/YellowJeil.jpeg';

const colors = {
  rojo: '#E00000',
  azul: '#0058E1',
  verde: '#1EC61F',
  amarillo: '#E8E300'
};

const Casilla = ({ num, bgColor = 'white', safe = false, corner = '' }: { num: number; bgColor?: string; safe?: boolean; corner?: string }) => {
  const getClipPath = () => {
    switch(corner) {
      case 'top-left': return 'polygon(50% 0, 100% 0, 100% 100%, 0 100%, 0 50%)';
      case 'top-right': return 'polygon(0 0, 50% 0, 100% 50%, 100% 100%, 0 100%)';
      case 'bottom-left': return 'polygon(0 0, 100% 0, 100% 100%, 50% 100%, 0 50%)';
      case 'bottom-right': return 'polygon(0 0, 100% 0, 100% 50%, 50% 100%, 0 100%)';
      default: return 'none';
    }
  };

  return (
    <div 
      className="w-full h-full border-2 border-gray-800 flex items-center justify-center font-bold relative"
      style={{ 
        backgroundColor: bgColor,
        clipPath: getClipPath(),
        fontSize: '25px'
      }}
    >
      {num}
      {safe && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="border-3 border-gray-700 rounded-full bg-transparent" style={{ width: '80px', height: '80px', borderWidth: '1px' }}></div>
        </div>
      )}
    </div>
  );
};

const Meta = ({ color }: { color: string }) => (
  <div 
    className="w-full h-full border-2 border-gray-800"
    style={{ 
      backgroundColor: color
    }}
  />
);

const Carcel = ({ img }: { img: string }) => (
  <div className="w-full h-full">
    <img src={img} alt="Carcel" style={{ width: '80%', height: '80%' }} className="object-cover" />
  </div>
);

const Centro = () => (
  <div className="w-full h-full flex items-center justify-center p-1">
    <img src={CenterImg} alt="Centro" className="w-full h-full object-cover" />
  </div>
);

const Board: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-2 sm:p-4">
      <div className="bg-white p-2 sm:p-4 rounded-xl shadow-2xl">
        <div
          className="grid gap-0"
          style={{
            gridTemplateColumns: 'repeat(19, 250px)',
            gridTemplateRows: 'repeat(19, 250px)',
          }}
        >
          
          {/* ========== CARCEL ROJA (5x5) ========== */}
          <div style={{gridRow: '5/11', gridColumn: '1/11'}}><Carcel img={RedJeil} /></div>
          
          {/* ========== BRAZO SUPERIOR (ROJO) ========== */}
          {/* Fila 1 */}
          <div style={{gridRow: '1', gridColumn: '9'}}><Casilla num={35} /></div>
          <div style={{gridRow: '1', gridColumn: '10'}}><Casilla num={34} /></div>
          <div style={{gridRow: '1', gridColumn: '11'}}><Casilla num={33} /></div>
          
          {/* Fila 2 */}
          <div style={{gridRow: '2', gridColumn: '9'}}><Casilla num={36} /></div>
          <div style={{gridRow: '2', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '2', gridColumn: '11'}}><Casilla num={32} /></div>
          
          {/* Fila 3 */}
          <div style={{gridRow: '3', gridColumn: '9'}}><Casilla num={37} /></div>
          <div style={{gridRow: '3', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '3', gridColumn: '11'}}><Casilla num={31} /></div>
          
          {/* Fila 4 */}
          <div style={{gridRow: '4', gridColumn: '9'}}><Casilla num={38} /></div>
          <div style={{gridRow: '4', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '4', gridColumn: '11'}}><Casilla num={30} /></div>
          
          {/* Fila 5 */}
          <div style={{gridRow: '5', gridColumn: '9'}}><Casilla num={39} bgColor={colors.rojo} /></div>
          <div style={{gridRow: '5', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '5', gridColumn: '11'}}><Casilla num={29} bgColor={colors.rojo}  /></div>
          
          {/* Fila 6 */}
          <div style={{gridRow: '6', gridColumn: '9'}}><Casilla num={40} /></div>
          <div style={{gridRow: '6', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '6', gridColumn: '11'}}><Casilla num={28} /></div>
          
          {/* Fila 7 */}
          <div style={{gridRow: '7', gridColumn: '9'}}><Casilla num={41} /></div>
          <div style={{gridRow: '7', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '7', gridColumn: '11'}}><Casilla num={27} /></div>
          
          {/* Fila 8 */}
          <div style={{gridRow: '8', gridColumn: '9'}}><Casilla num={42} /></div>
          <div style={{gridRow: '8', gridColumn: '10'}}><Meta color={colors.rojo} /></div>
          <div style={{gridRow: '8', gridColumn: '11'}}><Casilla num={26} /></div>
          
          {/* ========== CARCEL AZUL (5x5) ========== */}
          <div style={{gridRow: '5/10', gridColumn: '12/20'}}><Carcel img={BlueJeil} /></div>
          
          {/* ========== BRAZO IZQUIERDO (VERDE) ========== */}
          {/* Columna superior */}
          <div style={{gridRow: '9', gridColumn: '8'}}><Casilla num={43} /></div>
          <div style={{gridRow: '9', gridColumn: '7'}}><Casilla num={44} /></div>
          <div style={{gridRow: '9', gridColumn: '6'}}><Casilla num={45} /></div>
          <div style={{gridRow: '9', gridColumn: '5'}}><Casilla num={46} bgColor={colors.verde} /></div>
          <div style={{gridRow: '9', gridColumn: '4'}}><Casilla num={47} /></div>
          <div style={{gridRow: '9', gridColumn: '3'}}><Casilla num={48} /></div>
          <div style={{gridRow: '9', gridColumn: '2'}}><Casilla num={49} /></div>  
          <div style={{gridRow: '9', gridColumn: '1'}}><Casilla num={50} /></div>  

          {/*Metas verdes*/}
          <div style={{gridRow: '10', gridColumn: '8'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '7'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '6'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '5'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '4'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '3'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '2'}}><Meta color={colors.verde} /></div>
          <div style={{gridRow: '10', gridColumn: '1'}}><Casilla num={51} /></div>  
          {/* Columna inferior */}
          <div style={{gridRow: '11', gridColumn: '8'}}><Casilla num={59} /></div>
          <div style={{gridRow: '11', gridColumn: '7'}}><Casilla num={58} /></div>
          <div style={{gridRow: '11', gridColumn: '6'}}><Casilla num={57} /></div>
          <div style={{gridRow: '11', gridColumn: '5'}}><Casilla num={56} bgColor={colors.verde} /></div>
          <div style={{gridRow: '11', gridColumn: '4'}}><Casilla num={55} /></div>
          <div style={{gridRow: '11', gridColumn: '3'}}><Casilla num={54} /></div>
          <div style={{gridRow: '11', gridColumn: '2'}}><Casilla num={53} /></div>  
          <div style={{gridRow: '11', gridColumn: '1'}}><Casilla num={52} /></div>  
          
          {/* ========== CENTRO (3x3) ========== */}
          <div style={{gridRow: '9/12', gridColumn: '9/12'}}><Centro /></div>
          
          {/* ========== BRAZO DERECHO (AZUL) ========== */}
          {/* Columna superior */}
          <div style={{gridRow: '9', gridColumn: '12'}}><Casilla num={25} /></div>
          <div style={{gridRow: '9', gridColumn: '13'}}><Casilla num={24} /></div>
          <div style={{gridRow: '9', gridColumn: '14'}}><Casilla num={23} /></div>
          <div style={{gridRow: '9', gridColumn: '15'}}><Casilla num={22} bgColor={colors.azul} /></div>
          <div style={{gridRow: '9', gridColumn: '16'}}><Casilla num={21} /></div>
          <div style={{gridRow: '9', gridColumn: '17'}}><Casilla num={20} /></div>
          <div style={{gridRow: '9', gridColumn: '18'}}><Casilla num={19} /></div>  
          <div style={{gridRow: '9', gridColumn: '19'}}><Casilla num={18} /></div>  

          {/*Metas azules */}
          <div style={{gridRow: '10', gridColumn: '12'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '13'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '14'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '15'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '16'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '17'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '18'}}><Meta color={colors.azul} /></div>
          <div style={{gridRow: '10', gridColumn: '19'}}><Casilla num={17} /></div> 

          {/* Columna inferior */}
          <div style={{gridRow: '11', gridColumn: '12'}}><Casilla num={9} /></div>
          <div style={{gridRow: '11', gridColumn: '13'}}><Casilla num={10} /></div>
          <div style={{gridRow: '11', gridColumn: '14'}}><Casilla num={11} /></div>
          <div style={{gridRow: '11', gridColumn: '15'}}><Casilla num={12} bgColor={colors.azul} /></div>
          <div style={{gridRow: '11', gridColumn: '16'}}><Casilla num={13} /></div>
          <div style={{gridRow: '11', gridColumn: '17'}}><Casilla num={14} /></div>
          <div style={{gridRow: '11', gridColumn: '18'}}><Casilla num={15} /></div>  
          <div style={{gridRow: '11', gridColumn: '19'}}><Casilla num={16} /></div>  

          {/* ========== CARCEL VERDE (5x5) ========== */}
          <div style={{gridRow: '12/30', gridColumn: '3/11'}}><Carcel img={GreenJeil} /></div>
          
          {/* ========== BRAZO INFERIOR (AMARILLO) ========== */}
          {/* Fila 12 */}
          <div style={{gridRow: '12', gridColumn: '9'}}><Casilla num={60} /></div>
          <div style={{gridRow: '12', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '12', gridColumn: '11'}}><Casilla num={8} /></div>

          {/* Fila 13 */}
          <div style={{gridRow: '13', gridColumn: '9'}}><Casilla num={61} /></div>
          <div style={{gridRow: '13', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '13', gridColumn: '11'}}><Casilla num={7} /></div>

          {/* Fila 14 */}
          <div style={{gridRow: '14', gridColumn: '9'}}><Casilla num={62} /></div>
          <div style={{gridRow: '14', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '14', gridColumn: '11'}}><Casilla num={6} /></div>

          {/* Fila 15 */}
          <div style={{gridRow: '15', gridColumn: '9'}}><Casilla num={63} bgColor={colors.amarillo}/></div>
          <div style={{gridRow: '15', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '15', gridColumn: '11'}}><Casilla num={5} bgColor={colors.amarillo} /></div>

          {/* Fila 16 */}
          <div style={{gridRow: '16', gridColumn: '9'}}><Casilla num={64} /></div>
          <div style={{gridRow: '16', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '16', gridColumn: '11'}}><Casilla num={4} /></div>

          {/* Fila 17 */}
          <div style={{gridRow: '17', gridColumn: '9'}}><Casilla num={65} /></div>
          <div style={{gridRow: '17', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '17', gridColumn: '11'}}><Casilla num={3} /></div>

          {/* Fila 18 */}
          <div style={{gridRow: '18', gridColumn: '9'}}><Casilla num={66} /></div>
          <div style={{gridRow: '18', gridColumn: '10'}}><Meta color={colors.amarillo} /></div>
          <div style={{gridRow: '18', gridColumn: '11'}}><Casilla num={2} /></div>

          {/* Fila 19 */}
          <div style={{gridRow: '19', gridColumn: '9'}}><Casilla num={67} /></div>
          <div style={{gridRow: '19', gridColumn: '10'}}><Casilla num={68} /></div>
          <div style={{gridRow: '19', gridColumn: '11'}}><Casilla num={1} /></div>

          {/* ========== CARCEL AMARILLA (5x5) ========== */}
          <div style={{gridRow: '12/20', gridColumn: '12/50'}}><Carcel img={YellowJeil} /></div>
          
        </div>
      </div>
    </div>
  )
};

export default Board;