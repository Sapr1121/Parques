import React, { useState } from 'react';
import JoinRoomModal from '../components/JoinRoomModal';

const JoinRoom: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(true);
  const [joinedCode, setJoinedCode] = useState<string | null>(null);

  const handleClose = () => setModalOpen(false);

  const handleJoin = (code: string) => {
    setJoinedCode(code);
    setModalOpen(false);
    // Aquí puedes navegar, mostrar info, o conectar al WebSocket
    // Por ejemplo: navigate(`/board?code=${code}`);
  };

  return (
    <div>
      <JoinRoomModal
        isOpen={modalOpen}
        onClose={handleClose}
        onJoin={handleJoin}
      />
      {joinedCode && (
        <div className="mt-8 text-center text-lg font-bold text-green-700">
          ¡Te uniste a la sala {joinedCode}!
        </div>
      )}
    </div>
  );
};

export default JoinRoom;