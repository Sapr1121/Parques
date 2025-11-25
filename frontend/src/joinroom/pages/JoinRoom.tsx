import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import JoinRoomModal from '../components/JoinRoomModal';

const COLORS = ['amarillo', 'azul', 'rojo', 'verde'];

const colorStyles = {
  amarillo: 'bg-gradient-to-br from-yellow-300 to-yellow-500 hover:from-yellow-400 hover:to-yellow-600 shadow-yellow-500/50',
  azul: 'bg-gradient-to-br from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 shadow-blue-500/50',
  rojo: 'bg-gradient-to-br from-red-400 to-red-600 hover:from-red-500 hover:to-red-700 shadow-red-500/50',
  verde: 'bg-gradient-to-br from-green-400 to-green-600 hover:from-green-500 hover:to-green-700 shadow-green-500/50'
};

const emotionEmojis = {
  amarillo: '😄',
  azul: '😢',
  rojo: '😡',
  verde: '🤢'
};

const JoinRoom: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(true);
  const [selectedColor, setSelectedColor] = useState<string>(COLORS[0]);
  const navigate = useNavigate();

  const handleClose = () => setModalOpen(false);

  const handleJoin = (code: string, color: string, name: string) => {
    setModalOpen(false);
    console.log('✅ Unido a la sala, navegando al lobby...');
    navigate('/lobby', { state: { isAdmin: false } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-300 to-blue-300 relative overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-yellow-300 rounded-full opacity-30 blur-2xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-blue-400 rounded-full opacity-30 blur-2xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 right-10 w-36 h-36 bg-red-400 rounded-full opacity-30 blur-2xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-32 left-1/4 w-28 h-28 bg-green-400 rounded-full opacity-30 blur-2xl animate-pulse" style={{ animationDelay: '1.5s' }}></div>
      </div>

      <JoinRoomModal
        isOpen={modalOpen}
        onClose={handleClose}
        onJoin={handleJoin}
        selectedColor={selectedColor}
        setSelectedColor={setSelectedColor}
      />
      {/* El selector de color ahora solo está en el modal */}
    </div>
  );
};

export default JoinRoom;