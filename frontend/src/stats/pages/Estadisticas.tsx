import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { obtenerEstadisticas, obtenerSesion, haySesionActiva } from '../../auth/services/authService';

interface PartidaInfo {
  fecha: string;
  resultado: string;
  color_jugado: string;
  fichas_en_meta: number;
  turnos_jugados: number;
  tiempo_juego: number;
}

interface Stats {
  username: string;
  partidas_jugadas: number;
  partidas_ganadas: number;
  partidas_perdidas: number;
  tasa_victoria: number;
  fichas_totales_en_meta: number;
  ultimas_partidas: PartidaInfo[];
}

export default function Estadisticas() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<Stats | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!haySesionActiva()) {
      navigate('/auth');
      return;
    }

    const cargarEstadisticas = async () => {
      const sesion = obtenerSesion();
      if (!sesion) {
        navigate('/auth');
        return;
      }

      try {
        const resultado = await obtenerEstadisticas(sesion.usuario_id);
        if (resultado.exito && resultado.estadisticas) {
          setStats(resultado.estadisticas);
        } else {
          setError(resultado.mensaje);
        }
      } catch (err) {
        setError('Error al cargar las estadísticas');
      } finally {
        setCargando(false);
      }
    };

    cargarEstadisticas();
  }, [navigate]);

  const formatTiempo = (segundos: number) => {
    const mins = Math.floor(segundos / 60);
    const secs = segundos % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getColorClass = (color: string) => {
    const colores: { [key: string]: string } = {
      rojo: 'bg-red-500',
      azul: 'bg-blue-500',
      verde: 'bg-green-500',
      amarillo: 'bg-yellow-500',
    };
    return colores[color.toLowerCase()] || 'bg-gray-500';
  };

  const getResultadoClass = (resultado: string) => {
    return resultado.toLowerCase() === 'victoria'
      ? 'text-green-400 font-bold'
      : 'text-red-400';
  };

  if (cargando) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-white text-2xl">Cargando estadísticas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center">
          <p className="text-red-400 text-xl mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded-lg"
          >
            Volver al menú
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="text-white/70 hover:text-white flex items-center gap-2"
          >
            ← Volver
          </button>
          <h1 className="text-3xl font-bold text-white">
            📊 Mis Estadísticas
          </h1>
          <div className="w-20" /> {/* Spacer */}
        </div>

        {/* Tarjeta de Usuario */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-2">
            👤 {stats?.username}
          </h2>
        </div>

        {/* Estadísticas Generales */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 text-center">
            <div className="text-4xl font-bold text-white">
              {stats?.partidas_jugadas || 0}
            </div>
            <div className="text-white/70 text-sm">Partidas Jugadas</div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 text-center">
            <div className="text-4xl font-bold text-green-400">
              {stats?.partidas_ganadas || 0}
            </div>
            <div className="text-white/70 text-sm">Victorias</div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 text-center">
            <div className="text-4xl font-bold text-red-400">
              {stats?.partidas_perdidas || 0}
            </div>
            <div className="text-white/70 text-sm">Derrotas</div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 text-center">
            <div className="text-4xl font-bold text-yellow-400">
              {((stats?.tasa_victoria || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-white/70 text-sm">Tasa de Victoria</div>
          </div>

          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20 text-center col-span-2 md:col-span-2">
            <div className="text-4xl font-bold text-purple-400">
              {stats?.fichas_totales_en_meta || 0}
            </div>
            <div className="text-white/70 text-sm">Fichas Totales en Meta</div>
          </div>
        </div>

        {/* Últimas Partidas */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">
            🕐 Últimas 10 Partidas
          </h3>

          {stats?.ultimas_partidas && stats.ultimas_partidas.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-white/70 text-sm border-b border-white/20">
                    <th className="pb-3 text-left">Fecha</th>
                    <th className="pb-3 text-center">Color</th>
                    <th className="pb-3 text-center">Resultado</th>
                    <th className="pb-3 text-center">Fichas Meta</th>
                    <th className="pb-3 text-center">Turnos</th>
                    <th className="pb-3 text-center">Tiempo</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.ultimas_partidas.map((partida, index) => (
                    <tr key={index} className="text-white border-b border-white/10 last:border-0">
                      <td className="py-3 text-sm">
                        {new Date(partida.fecha).toLocaleDateString('es-ES', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td className="py-3 text-center">
                        <span
                          className={`inline-block w-6 h-6 rounded-full ${getColorClass(partida.color_jugado)}`}
                          title={partida.color_jugado}
                        />
                      </td>
                      <td className={`py-3 text-center ${getResultadoClass(partida.resultado)}`}>
                        {partida.resultado}
                      </td>
                      <td className="py-3 text-center">{partida.fichas_en_meta}/4</td>
                      <td className="py-3 text-center">{partida.turnos_jugados}</td>
                      <td className="py-3 text-center">{formatTiempo(partida.tiempo_juego)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center text-white/50 py-8">
              Aún no has jugado ninguna partida
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
