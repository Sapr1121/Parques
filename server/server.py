import socket
import threading
import json
import sys
import logging
import time
from game_manager import GameManager
import protocol as proto

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ParchisServer:
    def __init__(self, host="0.0.0.0", port=8001):
        self.host = host
        self.port = port
        self.server_socket = None
        self.game_manager = GameManager()
        self.running = False
        self.clientes_activos = set()
        
    def iniciar(self):
        """Inicia el servidor"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(proto.MAX_JUGADORES)
            self.running = True
            
            logger.info("="*60)
            logger.info("SERVIDOR DE PARCHÍS INICIADO".center(60))
            logger.info("="*60)
            logger.info(f"Escuchando en {self.host}:{self.port}")
            logger.info(f"Esperando jugadores (mín: {proto.MIN_JUGADORES}, máx: {proto.MAX_JUGADORES})")
            logger.info("="*60)
            
            accept_thread = threading.Thread(target=self.aceptar_conexiones)
            accept_thread.daemon = True
            accept_thread.start()
            
            try:
                accept_thread.join()
            except KeyboardInterrupt:
                logger.info("Recibida señal de interrupción...")
                self.detener()
                
        except Exception as e:
            logger.error(f"Error al iniciar servidor: {e}")
            sys.exit(1)
    
    def aceptar_conexiones(self):
        """Acepta nuevas conexiones de clientes"""
        while self.running:
            try:
                cliente_socket, addr = self.server_socket.accept()
                logger.info(f"Nueva conexión desde {addr}")
                
                self.clientes_activos.add(cliente_socket)
                
                cliente_thread = threading.Thread(
                    target=self.manejar_cliente,
                    args=(cliente_socket, addr)
                )
                cliente_thread.daemon = True
                cliente_thread.start()
                
            except socket.error as e:
                if self.running:
                    logger.error(f"Error aceptando conexión: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"Error inesperado: {e}")
    
    def manejar_cliente(self, cliente_socket, addr):
        """Maneja la comunicación con un cliente específico"""
        nombre = "Desconocido"
        try:
            logger.debug(f"Iniciando manejo de cliente {addr}")
            
            cliente_socket.settimeout(30.0)
            
            # Esperar mensaje de conexión
            data = self.recibir_mensaje(cliente_socket)
            if not data:
                logger.warning(f"No se recibió mensaje inicial de {addr}")
                return
            
            mensaje = self.parsear_mensaje(data)
            if not mensaje:
                logger.warning(f"Mensaje inicial inválido de {addr}")
                self.enviar(cliente_socket, proto.mensaje_error("JSON inválido"))
                return
            
            if mensaje["tipo"] != proto.MSG_CONECTAR:
                logger.warning(f"Protocolo inválido de {addr}: {mensaje.get('tipo', 'UNKNOWN')}")
                self.enviar(cliente_socket, proto.mensaje_error("Protocolo inválido"))
                return
            
            nombre = mensaje.get("nombre", f"Jugador_{addr[1]}")
            logger.info(f"Cliente {addr} solicita conectarse como '{nombre}'")
            
            # Agregar jugador
            color, error = self.game_manager.agregar_jugador(cliente_socket, nombre)
            
            if error:
                logger.warning(f"{nombre} no pudo conectarse: {error}")
                self.enviar(cliente_socket, proto.mensaje_error(error))
                return
            
            logger.info(f"{nombre} conectado como {color.upper()}")
            
            # Enviar bienvenida
            jugador_id = self.game_manager.clientes[cliente_socket]["id"]
            self.enviar(cliente_socket, proto.mensaje_bienvenida(color, jugador_id, nombre))
            
            # Notificar estado de espera
            conectados = len(self.game_manager.jugadores)
            self.broadcast(proto.mensaje_esperando(conectados, proto.MIN_JUGADORES))
            
            # Verificar si se puede iniciar el juego
            if not self.game_manager.juego_iniciado and self.game_manager.puede_iniciar():
                logger.info(f"¡Hay {conectados} jugadores! Iniciando juego...")
                self.iniciar_juego()
            
            cliente_socket.settimeout(None)
            
            # Loop principal de comunicación
            logger.debug(f"Iniciando loop de comunicación para {nombre}")
            while self.running:
                data = self.recibir_mensaje(cliente_socket)
                if not data:
                    logger.debug(f"Cliente {nombre} cerró conexión")
                    break
                
                mensaje = self.parsear_mensaje(data)
                if mensaje:
                    logger.debug(f"Mensaje recibido de {nombre}: {mensaje}")
                    self.procesar_mensaje(cliente_socket, mensaje)
                else:
                    logger.warning(f"Mensaje inválido de {nombre}")
                
        except socket.timeout:
            logger.warning(f"Timeout para cliente {addr}")
        except ConnectionResetError:
            logger.info(f"Cliente {addr} desconectado abruptamente")
        except Exception as e:
            logger.error(f"Error con cliente {addr}: {e}")
        
        finally:
            logger.debug(f"Limpiando cliente {nombre} ({addr})")
            self.limpiar_cliente(cliente_socket, nombre)
    
    def recibir_mensaje(self, cliente_socket):
        """Recibe un mensaje del cliente con manejo de errores"""
        try:
            data = cliente_socket.recv(4096)
            if not data:
                return None
            logger.debug(f"Datos recibidos: {len(data)} bytes")
            return data
        except socket.error as e:
            logger.debug(f"Error de socket al recibir: {e}")
            return None
    
    def parsear_mensaje(self, data):
        """Parsea un mensaje JSON con manejo de errores"""
        try:
            mensaje = json.loads(data.decode('utf-8'))
            logger.debug(f"JSON parseado: {mensaje}")
            return mensaje
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error parseando mensaje: {e}")
            return None
    
    def limpiar_cliente(self, cliente_socket, nombre):
        """Limpia los recursos de un cliente desconectado"""
        try:
            self.clientes_activos.discard(cliente_socket)
            
            nombre_real, color = self.game_manager.eliminar_jugador(cliente_socket)
            if nombre_real:
                logger.info(f"{nombre_real} ({color}) desconectado")
                self.broadcast(proto.crear_mensaje(
                    proto.MSG_JUGADOR_DESCONECTADO,
                    nombre=nombre_real,
                    color=color
                ))
                
                if (self.game_manager.juego_iniciado and 
                    not getattr(self.game_manager, 'juego_terminado', False)):
                    self.game_manager.manejar_desconexion_en_turno(cliente_socket)
                    time.sleep(0.1)
                    self.notificar_turno()
            
            cliente_socket.close()
            
        except Exception as e:
            logger.error(f"Error limpiando cliente: {e}")
    
    def procesar_mensaje(self, cliente_socket, mensaje):
        
        try:
            tipo = mensaje.get("tipo")
            cliente_info = cliente_socket.getpeername()
            logger.debug(f"Procesando {tipo} de {cliente_info}")
            
            if tipo == proto.MSG_LANZAR_DADOS:
                logger.info(f"LANZAR_DADOS recibido de {cliente_info}")
                self.procesar_lanzar_dados(cliente_socket)
            
            elif tipo == proto.MSG_SACAR_CARCEL:
                logger.info(f"SACAR_CARCEL recibido de {cliente_info}")
                self.procesar_sacar_carcel(cliente_socket)
            
            elif tipo == proto.MSG_MOVER_FICHA:
                ficha_id = mensaje.get("ficha_id", 0)
                logger.info(f"MOVER_FICHA recibido de {cliente_info}, ficha: {ficha_id}")
                self.procesar_mover_ficha(cliente_socket, ficha_id)
            
            else:
                logger.warning(f"Mensaje no reconocido de {cliente_info}: {tipo}")
                self.enviar(cliente_socket, proto.mensaje_error("Mensaje no reconocido"))
                
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            self.enviar(cliente_socket, proto.mensaje_error("Error interno del servidor"))

    def procesar_lanzar_dados(self, cliente_socket):
        
        cliente_info = cliente_socket.getpeername()
        logger.info(f"INICIANDO procesamiento de dados para {cliente_info}")
    
        try:
            # Verificar turno
            es_turno = self.game_manager.es_turno_de(cliente_socket)
            if not es_turno:
                error_msg = "No es tu turno"
                logger.warning(f"{error_msg} para {cliente_info}")
                self.enviar(cliente_socket, proto.mensaje_error(error_msg))
                return
        
            # Lanzar dados
            dado1, dado2, suma, es_doble = self.game_manager.lanzar_dados_safe()
            logger.info(f"Dados generados: [{dado1}] [{dado2}] = {suma}, dobles: {es_doble}")
        
            # Enviar mensaje de dados
            mensaje_dados = proto.mensaje_dados(dado1, dado2, suma, es_doble)
            self.broadcast(mensaje_dados)
            logger.info(f"Dados enviados exitosamente")
        
            # Si salió doble, liberar TODAS las fichas automáticamente
            if es_doble:
                logger.info(f"Dobles detectados - liberando TODAS las fichas automáticamente...")
            
                exito, resultado = self.game_manager.sacar_todas_fichas_carcel(cliente_socket)
            
                if exito:
                    info = self.game_manager.clientes[cliente_socket]
                    fichas_liberadas = resultado.get("fichas_liberadas", [])
                
                    # Notificar liberación de cada ficha
                    for ficha_id in fichas_liberadas:
                        self.broadcast(proto.crear_mensaje(
                            proto.MSG_MOVIMIENTO_OK,
                            nombre=info["nombre"],
                            color=info["color"],
                            ficha_id=ficha_id,
                            desde=-1,
                            hasta=resultado.get("posicion", 0),
                            accion="liberar_ficha"
                        ))
                
                    logger.info(f"{len(fichas_liberadas)} fichas liberadas para {info['nombre']}")
                    self.broadcast_tablero()
                
                    self.broadcast(proto.crear_mensaje(
                        proto.MSG_INFO,
                        mensaje=f"¡{info['nombre']} sacó dobles! Todas las fichas liberadas. Mantiene el turno."
                    ))
                    
                    
                    logger.info(f"{info['nombre']} mantiene el turno - reenviando notificación")
                    time.sleep(0.1) 
                    self.broadcast(proto.mensaje_turno(info["nombre"], info["color"]))
            
            else:
                
                logger.info(f"Sin dobles - verificando si puede hacer acciones...")
            
                
                if self.game_manager.necesita_pasar_turno_automaticamente(cliente_socket):
                    info = self.game_manager.clientes[cliente_socket]
                
                    
                    logger.info(f"{info['nombre']} no puede hacer ninguna acción - pasando turno automáticamente")
                
                    self.broadcast(proto.crear_mensaje(
                        proto.MSG_INFO,
                        mensaje=f"{info['nombre']} no puede hacer ninguna acción. Turno pasado automáticamente."
                    ))
                
                    
                    if self.game_manager.forzar_avance_turno():
                        logger.info("Turno forzado - notificando al siguiente jugador")
                        time.sleep(0.2)
                        
                        
                        self.broadcast_tablero()
                        
                        
                        time.sleep(0.1)
                        
                        
                        self.notificar_turno()
                        
                        logger.info("Notificación de turno enviada al siguiente jugador")
                
                    return
                else:
                    logger.info(f"Jugador puede mover fichas - esperando acción")
        
            logger.info(f"COMPLETADO: Dados [{dado1}] [{dado2}] = {suma} {'(DOBLES!)' if es_doble else ''}")
        
        except Exception as e:
            logger.error(f"ERROR CRÍTICO en procesamiento de dados: {e}")
            self.enviar(cliente_socket, proto.mensaje_error("Error generando dados"))

    def procesar_sacar_carcel(self, cliente_socket):
        """Procesa el intento de sacar una ficha de la cárcel"""
        exito, resultado = self.game_manager.sacar_de_carcel(cliente_socket)
        
        if not exito:
            logger.warning(f"Error sacando de cárcel: {resultado}")
            self.enviar(cliente_socket, proto.mensaje_error(resultado))
            return
        
        info = self.game_manager.clientes[cliente_socket]
        color = info["color"]
        indice_color = proto.COLORES.index(color)
        salida = self.game_manager.tablero.salidas[indice_color]
        
        self.broadcast(proto.crear_mensaje(
            proto.MSG_MOVIMIENTO_OK,
            nombre=info["nombre"],
            color=color,
            ficha_id=resultado.get("ficha_id", 0),
            desde=-1,
            hasta=salida
        ))
        
        logger.info(f"{info['nombre']} sacó ficha de la cárcel")
        
        self.broadcast_tablero()
        
        
        if self.game_manager.debe_avanzar_turno_ahora():
            turno_avanzado = self.game_manager.avanzar_turno()
            if turno_avanzado:
                time.sleep(0.1)
                self.notificar_turno()
            else:
                
                logger.info("Jugador mantiene turno después de sacar de cárcel")
                time.sleep(0.1)
                self.broadcast(proto.mensaje_turno(info["nombre"], info["color"]))
    
    def procesar_mover_ficha(self, cliente_socket, ficha_id):
        
        exito, resultado = self.game_manager.mover_ficha(cliente_socket, ficha_id)
        
        if not exito:
            logger.warning(f"Error moviendo ficha: {resultado}")
            self.enviar(cliente_socket, proto.mensaje_error(resultado))
            return
        
        info = self.game_manager.clientes[cliente_socket]
        
        self.broadcast(proto.crear_mensaje(
            proto.MSG_MOVIMIENTO_OK,
            nombre=info["nombre"],
            color=info["color"],
            ficha_id=ficha_id,
            desde=resultado["desde"],
            hasta=resultado["hasta"]
        ))
        
        logger.info(f"🎮 {info['nombre']} movió ficha {ficha_id}")
        
        self.broadcast_tablero()
        
        # Verificar victoria
        if self.game_manager.verificar_victoria(cliente_socket):
            self.broadcast(proto.mensaje_victoria(info["nombre"], info["color"]))
            logger.info(f"¡{info['nombre']} ({info['color']}) HA GANADO!")
            self.game_manager.juego_terminado = True
            return
        
        
        if self.game_manager.debe_avanzar_turno_ahora():
            turno_avanzado = self.game_manager.avanzar_turno()
            if turno_avanzado:
                logger.info("Turno avanzado después de mover ficha")
                time.sleep(0.1)
                self.notificar_turno()
            else:
                # Mantiene turno - permitir lanzar dados de nuevo
                logger.info("Jugador mantiene turno - puede lanzar dados nuevamente")
                time.sleep(0.1)
                self.broadcast(proto.mensaje_turno(info["nombre"], info["color"]))
    
    def iniciar_juego(self):
        """Inicia el juego"""
        logger.info("Iniciando juego...")
        
        self.game_manager.iniciar_juego()
        
        jugadores_info = self.game_manager.obtener_info_jugadores()
        
        self.broadcast(proto.crear_mensaje(
            proto.MSG_INICIO_JUEGO,
            jugadores=jugadores_info
        ))
        
        self.broadcast_tablero()
        time.sleep(0.1)  
        self.notificar_turno()
        
        logger.info("Juego iniciado exitosamente")
    
    def notificar_turno(self):
        
        jugador_actual = self.game_manager.obtener_jugador_actual_safe()
        if not jugador_actual:
            logger.warning("No se pudo obtener jugador actual")
            return
        
        # Buscar el cliente correspondiente al jugador actual
        cliente_encontrado = None
        info_encontrada = None
        
        for cliente_sock, info in self.game_manager.clientes.items():
            if info["jugador"] == jugador_actual:
                cliente_encontrado = cliente_sock
                info_encontrada = info
                break
        
        if not cliente_encontrado or not info_encontrada:
            logger.error("No se encontró cliente para el jugador actual")
            return
        
        # Crear y enviar mensaje de turno
        mensaje_turno = proto.mensaje_turno(info_encontrada["nombre"], info_encontrada["color"])
        
        logger.info(f"NOTIFICANDO TURNO: {info_encontrada['nombre']} ({info_encontrada['color']})")
        logger.debug(f"Mensaje turno: {mensaje_turno}")
        
        # Enviar a todos los clientes
        self.broadcast(mensaje_turno)
        
        logger.info(f"Notificación de turno enviada a todos los clientes")
    
    def broadcast_tablero(self):
        """Envía el estado del tablero a todos los clientes"""
        try:
            estado = self.game_manager.obtener_estado_tablero()
            mensaje_tablero = proto.crear_mensaje(proto.MSG_TABLERO, **estado)
            self.broadcast(mensaje_tablero)
            logger.debug("Estado del tablero enviado")
        except Exception as e:
            logger.error(f"Error enviando estado del tablero: {e}")
    
    def enviar(self, cliente_socket, mensaje):
        """Envía un mensaje a un cliente específico con debug"""
        try:
            if cliente_socket in self.clientes_activos:
                data = json.dumps(mensaje, ensure_ascii=False).encode('utf-8')
                logger.debug(f"Enviando a {cliente_socket.getpeername()}: {mensaje}")
                cliente_socket.send(data)
                logger.debug(f"Mensaje enviado exitosamente")
            else:
                logger.warning(f"Intento de enviar a cliente inactivo")
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            self.clientes_activos.discard(cliente_socket)
    
    def broadcast(self, mensaje, excluir=None):
        
        logger.debug(f"BROADCAST a {len(self.game_manager.clientes)} clientes: {mensaje}")
        
        if not self.game_manager.clientes:
            logger.warning("No hay clientes para broadcast")
            return
        
        clientes_desconectados = []
        enviados_exitosos = 0
        
        for cliente_socket in list(self.game_manager.clientes.keys()):
            if cliente_socket != excluir:
                try:
                    self.enviar(cliente_socket, mensaje)
                    enviados_exitosos += 1
                except Exception as e:
                    logger.error(f"Error en broadcast: {e}")
                    clientes_desconectados.append(cliente_socket)
        
        logger.debug(f"Broadcast completado: {enviados_exitosos} enviados exitosamente")
        
        # Limpiar clientes desconectados
        for cliente_socket in clientes_desconectados:
            self.limpiar_cliente(cliente_socket, "Desconocido")
    
    def detener(self):
        """Detiene el servidor"""
        logger.info("🛑 Deteniendo servidor...")
        self.running = False
        
        for cliente_socket in list(self.clientes_activos):
            try:
                cliente_socket.close()
            except:
                pass
        
        if self.server_socket:
            self.server_socket.close()
        
        logger.info("✅ Servidor detenido")


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8001
    
    servidor = ParchisServer(HOST, PORT)
    
    try:
        servidor.iniciar()
    except KeyboardInterrupt:
        logger.info("Interrupción recibida...")
        servidor.detener()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        servidor.detener()
