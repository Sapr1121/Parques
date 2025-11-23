import React from 'react';
import { useNavigate } from 'react-router-dom';

const MainMenu = () => {
  const navigate = useNavigate();

  const handleCreateRoom = () => {
    console.log('Crear Sala');
    navigate('/create-room');
  };

  const handleJoinWithCode = () => {
    console.log('Unirse con Código');
    navigate('/join-room');
  };

  const handleExit = () => {
    console.log('Salir');
    window.close();
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden p-4"
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
      
      {/* Partículas de fondo animadas */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute w-64 h-64 sm:w-80 sm:h-80 lg:w-96 lg:h-96 bg-yellow-300 rounded-full opacity-20 blur-3xl animate-pulse" 
          style={{ top: '-10%', left: '-10%', animationDuration: '4s' }}></div>
        <div className="absolute w-56 h-56 sm:w-72 sm:h-72 lg:w-80 lg:h-80 bg-red-400 rounded-full opacity-20 blur-3xl animate-pulse" 
          style={{ top: '60%', right: '-10%', animationDuration: '5s' }}></div>
        <div className="absolute w-48 h-48 sm:w-64 sm:h-64 lg:w-72 lg:h-72 bg-blue-400 rounded-full opacity-20 blur-3xl animate-pulse" 
          style={{ bottom: '-10%', left: '30%', animationDuration: '6s' }}></div>
        <div className="absolute w-40 h-40 sm:w-56 sm:h-56 lg:w-64 lg:h-64 bg-green-400 rounded-full opacity-20 blur-3xl animate-pulse" 
          style={{ top: '20%', right: '20%', animationDuration: '7s' }}></div>
      </div>

      {/* Contenedor principal */}
      <div className="relative z-10 text-center w-full max-w-2xl">
        
        {/* Emociones de Intensamente como decoración */}
        <div className="absolute -top-8 sm:-top-12 left-0 right-0 flex justify-center space-x-2 sm:space-x-4 text-4xl sm:text-6xl md:text-7xl opacity-90">
          <span className="animate-bounce" style={{ animationDelay: '0s', animationDuration: '2s' }}>😊</span>
          <span className="animate-bounce" style={{ animationDelay: '0.2s', animationDuration: '2s' }}>😢</span>
          <span className="animate-bounce" style={{ animationDelay: '0.4s', animationDuration: '2s' }}>😡</span>
          <span className="animate-bounce" style={{ animationDelay: '0.6s', animationDuration: '2s' }}>😰</span>
          <span className="animate-bounce" style={{ animationDelay: '0.8s', animationDuration: '2s' }}>🤢</span>
        </div>

        {/* Título */}
        <div className="mb-8 sm:mb-12 mt-16 sm:mt-20 animate-bounce" style={{ animationDuration: '2s' }}>
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-black text-white mb-2 sm:mb-4 drop-shadow-2xl"
            style={{
              textShadow: '3px 3px 0px rgba(0,0,0,0.3), 6px 6px 15px rgba(0,0,0,0.2)',
              fontFamily: 'Arial Black, sans-serif'
            }}>
            PARQUIX
          </h1>
          <p className="text-xl sm:text-2xl md:text-3xl font-bold text-yellow-200 drop-shadow-lg"
            style={{
              textShadow: '2px 2px 4px rgba(0,0,0,0.4)'
            }}>
            ¡Bienvenido!
          </p>
          <p className="text-sm sm:text-base md:text-lg text-white/80 mt-2">
            Un viaje a través de las emociones
          </p>
        </div>

        {/* Botones */}
        <div className="space-y-4 sm:space-y-6">

          {/* Botón Crear Sala */}
          <button
            onClick={handleCreateRoom}
            className="w-full py-4 sm:py-6 px-6 sm:px-8 rounded-2xl font-black text-lg sm:text-xl md:text-2xl transform transition-all duration-200 hover:scale-105 sm:hover:scale-110 hover:rotate-1 active:scale-95 shadow-2xl"
            style={{
              background: 'linear-gradient(135deg, #ffd93d 0%, #f9ca24 100%)',
              color: '#2c3e50',
              textShadow: '1px 1px 2px rgba(255,255,255,0.5)',
              border: '4px solid rgba(255,255,255,0.5)'
            }}>
            <span className="text-2xl sm:text-3xl mr-2"></span>
            CREAR SALA
          </button>

          {/* Botón Unirse con Código*/}
          <button
            onClick={handleJoinWithCode}
            className="w-full py-4 sm:py-6 px-6 sm:px-8 rounded-2xl font-black text-lg sm:text-xl md:text-2xl transform transition-all duration-200 hover:scale-105 sm:hover:scale-110 hover:-rotate-1 active:scale-95 shadow-2xl"
            style={{
              background: 'linear-gradient(135deg, #4facfe 0%, #00a8e8 100%)',
              color: 'white',
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
              border: '4px solid rgba(255,255,255,0.3)'
            }}>
            <span className="text-2xl sm:text-3xl mr-2"></span>
            UNIRSE CON CÓDIGO
          </button>

          {/* Botón Salir */}
          <button
            onClick={handleExit}
            className="w-full py-3 sm:py-5 px-6 sm:px-8 rounded-2xl font-bold text-base sm:text-lg md:text-xl transform transition-all duration-200 hover:scale-105 active:scale-95 shadow-xl"
            style={{
              background: 'linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%)',
              color: 'white',
              textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
              border: '3px solid rgba(255,255,255,0.4)'
            }}>
            <span className="text-xl sm:text-2xl mr-2"></span>
            SALIR
          </button>
        </div>

        {/* Memoria central  */}
        <div className="mt-8 sm:mt-16 flex justify-center space-x-2 sm:space-x-4">
          <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-yellow-400 animate-bounce shadow-lg" style={{ animationDelay: '0s' }}></div>
          <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-blue-400 animate-bounce shadow-lg" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-red-400 animate-bounce shadow-lg" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-purple-400 animate-bounce shadow-lg" style={{ animationDelay: '0.3s' }}></div>
          <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-green-400 animate-bounce shadow-lg" style={{ animationDelay: '0.4s' }}></div>
        </div>

        {/* Islas de la personalidad*/}
        <div className="mt-4 sm:mt-6 text-xs sm:text-sm text-white/60">
          Explora las islas de la diversión 
        </div>
      </div>

      {/* Estrellas y memorias flotantes */}
      <div className="hidden sm:block">
        <div className="absolute top-10 left-10 lg:left-20 text-4xl sm:text-5xl lg:text-6xl animate-pulse opacity-80">💛</div>
        <div className="absolute top-32 right-20 lg:right-32 text-3xl sm:text-4xl lg:text-5xl animate-pulse opacity-60" style={{ animationDelay: '1s' }}>💙</div>
        <div className="absolute bottom-20 left-20 lg:left-40 text-3xl sm:text-4xl animate-pulse opacity-70" style={{ animationDelay: '2s' }}>❤️</div>
        <div className="absolute bottom-40 right-10 lg:right-20 text-3xl sm:text-4xl lg:text-5xl animate-pulse opacity-50" style={{ animationDelay: '1.5s' }}>💜</div>
      </div>
      
      {/* Versión móvil de decoraciones */}
      <div className="sm:hidden">
        <div className="absolute top-5 left-5 text-3xl animate-pulse opacity-80">💛</div>
        <div className="absolute top-5 right-5 text-3xl animate-pulse opacity-60" style={{ animationDelay: '1s' }}>💙</div>
        <div className="absolute bottom-5 left-5 text-3xl animate-pulse opacity-70" style={{ animationDelay: '2s' }}>❤️</div>
        <div className="absolute bottom-5 right-5 text-3xl animate-pulse opacity-50" style={{ animationDelay: '1.5s' }}>💜</div>
      </div>
    </div>
  );
};

export default MainMenu;