import React, { useState } from 'react';

interface DiceRollerProps {
  onRoll: (value: number) => void;
  disabled?: boolean;
}

const DiceRoller: React.FC<DiceRollerProps> = ({ onRoll, disabled }) => {
  const [rolling, setRolling] = useState(false);
  const [dice, setDice] = useState<[number, number] | null>(null);

  const handleRoll = () => {
    if (disabled || rolling) return;
    setRolling(true);

    try {
      let animationCount = 0;
      const animationInterval = setInterval(() => {
        setDice([
          Math.floor(Math.random() * 6) + 1,
          Math.floor(Math.random() * 6) + 1,
        ]);
        animationCount++;
        if (animationCount >= 10) {
          clearInterval(animationInterval);

          // Resultado final
          const dado1 = Math.floor(Math.random() * 6) + 1;
          const dado2 = Math.floor(Math.random() * 6) + 1;
          setDice([dado1, dado2]);
          setRolling(false);
          onRoll(dado1); // Enviamos dado1, el componente padre genera dado2
        }
      }, 80);
    } catch (error) {
      console.error('Error al tirar los dados:', error);
      setRolling(false); // Asegurar que el estado se restablezca
    }
  };

  // Emoji de dado según valor
  const getDiceEmoji = (value: number) => {
    const emojis = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    return emojis[value - 1] || '🎲';
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={handleRoll}
        disabled={disabled || rolling}
        className={`px-8 py-4 rounded-2xl font-bold text-xl bg-gradient-to-br from-yellow-300 to-orange-400 shadow-xl transition-all border-4 border-yellow-500 ${
          disabled || rolling 
            ? 'opacity-50 cursor-not-allowed' 
            : 'hover:scale-110 hover:shadow-2xl active:scale-95'
        }`}
      >
        {rolling ? '🎲 Tirando...' : '🎲 ¡Tirar Dados!'}
      </button>
      
      {dice && (
        <div className={`flex gap-4 ${rolling ? 'animate-bounce' : 'animate-pulse'}`}>
          <div className="text-6xl bg-white rounded-xl p-3 shadow-lg border-4 border-gray-300">
            {getDiceEmoji(dice[0])}
          </div>
          <div className="text-6xl bg-white rounded-xl p-3 shadow-lg border-4 border-gray-300">
            {getDiceEmoji(dice[1])}
          </div>
        </div>
      )}
      
      {dice && !rolling && (
        <div className="text-2xl font-extrabold text-purple-700">
          Total: {dice[0] + dice[1]}
        </div>
      )}
    </div>
  );
};

export default DiceRoller;
