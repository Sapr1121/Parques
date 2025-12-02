import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registrarUsuario, loginUsuario, guardarSesion } from '../services/authService';

export default function LoginRegister() {
  const navigate = useNavigate();
  const [modo, setModo] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      const resultado = await loginUsuario(username, password);
      
      if (resultado.exito && resultado.usuario_id !== null) {
        guardarSesion(username, resultado.usuario_id);
        navigate('/');
      } else {
        setError(resultado.mensaje);
      }
    } catch (err) {
      setError('Error al conectar con el servidor');
    } finally {
      setCargando(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      const resultado = await registrarUsuario(username, password, email);
      
      if (resultado.exito) {
        // Después de registrar, hacer login automático
        const loginResult = await loginUsuario(username, password);
        if (loginResult.exito && loginResult.usuario_id !== null) {
          guardarSesion(username, loginResult.usuario_id);
          navigate('/');
        } else {
          // Si falla el login automático, mostrar mensaje y cambiar a modo login
          setError('Registro exitoso. Por favor inicia sesión.');
          setModo('login');
          setPassword('');
        }
      } else {
        setError(resultado.mensaje);
      }
    } catch (err) {
      setError('Error al conectar con el servidor');
    } finally {
      setCargando(false);
    }
  };

  const handleInvitado = () => {
    // Continuar sin registrarse
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 w-full max-w-md border border-white/20">
        <h1 className="text-4xl font-bold text-white text-center mb-2">
          🎲 Parqués
        </h1>
        <p className="text-white/70 text-center mb-8">
          {modo === 'login' ? 'Inicia sesión para guardar tu progreso' : 'Regístrate para guardar tus estadísticas'}
        </p>

        {/* Pestañas */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => {
              setModo('login');
              setError('');
            }}
            className={`flex-1 py-3 rounded-lg font-semibold transition-all ${
              modo === 'login'
                ? 'bg-white text-purple-900 shadow-lg'
                : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            Iniciar Sesión
          </button>
          <button
            onClick={() => {
              setModo('register');
              setError('');
            }}
            className={`flex-1 py-3 rounded-lg font-semibold transition-all ${
              modo === 'register'
                ? 'bg-white text-purple-900 shadow-lg'
                : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            Registrarse
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={modo === 'login' ? handleLogin : handleRegister} className="space-y-4">
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Usuario
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/30 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50"
              placeholder="Tu nombre de usuario"
              required
              disabled={cargando}
            />
          </div>

          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/30 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50"
              placeholder="Tu contraseña"
              required
              disabled={cargando}
            />
          </div>

          {modo === 'register' && (
            <div>
              <label className="block text-white text-sm font-medium mb-2">
                Email (opcional)
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/30 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50"
                placeholder="tu@email.com"
                disabled={cargando}
              />
            </div>
          )}

          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-white px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={cargando}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-6 rounded-lg transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cargando ? 'Procesando...' : modo === 'login' ? 'Iniciar Sesión' : 'Registrarse'}
          </button>
        </form>

        {/* Opción de continuar como invitado */}
        <div className="mt-6 pt-6 border-t border-white/20">
          <button
            onClick={handleInvitado}
            disabled={cargando}
            className="w-full bg-white/10 hover:bg-white/20 text-white font-semibold py-3 px-6 rounded-lg transition-all disabled:opacity-50"
          >
            Continuar como Invitado
          </button>
          <p className="text-white/50 text-xs text-center mt-2">
            No se guardarán tus estadísticas
          </p>
        </div>
      </div>
    </div>
  );
}
