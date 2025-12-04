import asyncio
import websockets
import json
import logging
import inspect
import sys
import os
from game_manager import GameManager
import protocol as proto
import time

# Configurar path para importar DatabaseManager
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DatabaseManager



# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
def debug_callable(func):
    """Debugging helper para ver la firma de una función"""
    sig = inspect.signature(func)
    logger.critical(f"🔍 CALLABLE DEBUG:")
    logger.critical(f"   Nombre: {func.__name__}")
    logger.critical(f"   Tipo: {type(func)}")
    logger.critical(f"   Parámetros: {sig}")
    logger.critical(f"   Es coroutine: {inspect.iscoroutinefunction(func)}")
    return func


class ParchisServer:
    def __init__(self, host="0.0.0.0", port=8001, modo_embebido=False):
        """Constructor - Sin cambios importantes"""
        self.host = host
        self.port = port
        self.game_manager = GameManager()
        self.running = False
        self.clientes_activos = set()
        self.modo_embebido = modo_embebido
        
        # Inicializar el gestor de base de datos
        self.db_manager = DatabaseManager()
        
    async def iniciar(self):
        """Inicia el servidor WebSocket"""
        try:
            self.running = True
            
            logger.info("="*60)
            logger.info("SERVIDOR DE PARCHÍS WEBSOCKET INICIADO".center(60))
            logger.info("="*60)
            logger.info(f"Escuchando en ws://{self.host}:{self.port}")
            logger.info(f"Esperando jugadores (mín: {proto.MIN_JUGADORES}, máx: {proto.MAX_JUGADORES})")
            logger.info("="*60)
            
            # ✅ CORRECCIÓN: Handler sin argumento 'path' para websockets 15.x
            async def handler(websocket):
                logger.info(f"🔍 Nueva conexión desde {websocket.remote_address}")
                try:
                    # Llamar al método sin 'path'
                    await self.manejar_cliente(websocket)
                except Exception as e:
                    logger.error(f"🔍 Error en handler: {e}", exc_info=True)
                    raise
            
            logger.info("🔍 Iniciando websockets.serve()")
            
            async with websockets.serve(
                handler,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=10
            ):
                logger.info("✅ Servidor WebSocket escuchando...")
                await asyncio.Future()  # Mantener servidor corriendo
                
        except Exception as e:
            logger.critical(f"🔍 ERROR CRÍTICO en iniciar(): {e}", exc_info=True)
            raise
        
    async def manejar_cliente(self, websocket):
        """Maneja la comunicación con un cliente específico via WebSocket"""
        nombre = "Desconocido"
        conectado_correctamente = False
        addr = None
        
        try:
            # Obtener dirección de forma segura
            try:
                addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            except Exception:
                addr = "unknown"
            
            logger.debug(f"Iniciando manejo de cliente {addr}")
            
            # ⚡ IMPORTANTE: Agregar a clientes activos DESPUÉS del handshake
            # No aquí, para evitar conexiones fantasma
            
            async for mensaje_str in websocket:
                try:
                    mensaje = json.loads(mensaje_str)
                    tipo = mensaje.get("tipo")
                    
                    if not conectado_correctamente:
                        # 🆕 PERMITIR MSG_SYNC_REQUEST antes del handshake
                        if tipo == proto.MSG_SYNC_REQUEST:
                            logger.debug(f"SYNC_REQUEST (pre-handshake) recibido de {addr}")
                            
                            t1 = mensaje.get("t1")
                            t2 = time.time()
                            t3 = time.time()
                            
                            respuesta = proto.mensaje_sync_response(t1, t2, t3)
                            
                            # Enviar directamente (sin usar self.enviar que verifica clientes_activos)
                            try:
                                mensaje_json = json.dumps(respuesta, ensure_ascii=False)
                                await websocket.send(mensaje_json)
                                logger.debug(f"SYNC_RESPONSE enviado (pre-handshake)")
                            except Exception as e:
                                logger.error(f"Error enviando SYNC_RESPONSE pre-handshake: {e}")
                            
                            continue  # ← Continuar esperando más mensajes
                        
                        # 🆕 PERMITIR MSG_SOLICITAR_COLORES antes del handshake
                        if tipo == proto.MSG_SOLICITAR_COLORES:
                            logger.debug(f"SOLICITAR_COLORES (pre-handshake) recibido de {addr}")
                            
                            colores = self.game_manager.obtener_colores_disponibles()
                            
                            try:
                                respuesta = proto.mensaje_colores_disponibles(colores)
                                mensaje_json = json.dumps(respuesta, ensure_ascii=False)
                                await websocket.send(mensaje_json)
                                logger.debug(f"COLORES_DISPONIBLES enviado (pre-handshake): {colores}")
                            except Exception as e:
                                logger.error(f"Error enviando COLORES_DISPONIBLES pre-handshake: {e}")
                            
                            continue  # ← Continuar esperando más mensajes
                        
                        # 🆕 PERMITIR mensajes de autenticación antes del handshake
                        if tipo == proto.MSG_REGISTRAR_USUARIO:
                            await self.procesar_registro_usuario(websocket, mensaje)
                            continue
                        
                        if tipo == proto.MSG_LOGIN_USUARIO:
                            await self.procesar_login_usuario(websocket, mensaje)
                            continue
                        
                        if tipo == proto.MSG_OBTENER_ESTADISTICAS:
                            await self.procesar_obtener_estadisticas(websocket, mensaje)
                            continue
                        
                        # Si no es ninguno de los mensajes permitidos antes de conectar
                        if tipo != proto.MSG_CONECTAR:
                            logger.warning(f"Protocolo inválido de {addr}: {tipo}")
                            await self.enviar(websocket, proto.mensaje_error("Protocolo inválido: se esperaba CONECTAR"))
                            await websocket.close(code=1008, reason="Protocolo inválido")
                            return
                        
                        # ============ PROCESAR MSG_CONECTAR ============
                        nombre = mensaje.get("nombre", "").strip()
                        color_elegido = mensaje.get("color", None)  # 🆕 Obtener color del mensaje
                        usuario_id = mensaje.get("usuario_id", None)  # 🆕 ID de usuario de la BD
                        
                        if not nombre:
                            nombre = f"Jugador_{websocket.remote_address[1]}"
                        
                        logger.info(f"Cliente {addr} solicita conectarse como '{nombre}' con color '{color_elegido}' (usuario_id={usuario_id})")
                        
                        # Agregar jugador CON el color elegido y usuario_id
                        color, error, es_admin, es_host = self.game_manager.agregar_jugador(websocket, nombre, color_elegido, usuario_id)
                        
                        if error:
                            logger.warning(f"{nombre} no pudo conectarse: {error}")
                            await self.enviar(websocket, proto.mensaje_error(error))
                            await websocket.close(code=1008, reason=error)
                            return
                        
                        # ✅ AHORA SÍ agregamos a clientes activos
                        self.clientes_activos.add(websocket)
                        
                        logger.info(f"{nombre} conectado como {color.upper()} (admin={es_admin})")
                        
                        # Enviar bienvenida
                        jugador_id = self.game_manager.clientes[websocket]["id"]
                        await self.enviar(websocket, proto.mensaje_bienvenida(color, jugador_id, nombre))
                        
                        # Notificar estado con lista de jugadores
                        conectados = len(self.game_manager.jugadores)
                        jugadores_lista = self.game_manager.obtener_info_jugadores()
                        await self.broadcast(proto.mensaje_esperando(conectados, proto.MIN_JUGADORES, jugadores_lista))
                        
                        # ⭐ NUEVO: Inicio automático con 4 jugadores
                        if conectados == proto.MAX_JUGADORES:
                            logger.info(f"🎊 Se alcanzó el máximo de jugadores ({proto.MAX_JUGADORES}). Iniciando automáticamente...")
                            await self.broadcast(proto.mensaje_info(
                                f"¡Sala completa con {proto.MAX_JUGADORES} jugadores! Iniciando partida automáticamente..."
                            ))
                            await asyncio.sleep(1)  # Breve pausa para que los jugadores lean el mensaje
                            await self.iniciar_determinacion()
                        # Mensajes de admin (solo si no se inició automáticamente)
                        elif es_admin:
                            await self.enviar(websocket, proto.mensaje_info(
                                "Eres el administrador. Para iniciar la partida envía MSG_LISTO. "
                                f"Se requiere al menos {proto.MIN_JUGADORES} jugadores. "
                                f"Con {proto.MAX_JUGADORES} jugadores se inicia automáticamente.", 
                                es_admin=True
                            ))
                            await self.broadcast(proto.mensaje_info(
                                f"{nombre} es el administrador y podrá iniciar la partida cuando esté listo."
                            ))
                        else:
                            admin_sock = getattr(self.game_manager, "admin_cliente", None)
                            if admin_sock:
                                admin_info = self.game_manager.clientes.get(admin_sock, {})
                                admin_nombre = admin_info.get("nombre", "Administrador")
                                await self.enviar(websocket, proto.mensaje_info(
                                    f"El administrador actual es: {admin_nombre}"
                                ))
                        
                        conectado_correctamente = True
                        continue
                                        
                    # ============ MENSAJES NORMALES ============
                    if conectado_correctamente:
                        logger.debug(f"Procesando mensaje de {nombre}: {mensaje}")
                        await self.procesar_mensaje(websocket, mensaje)
                    
                    elif tipo == proto.MSG_DEBUG_FORZAR_TRES_DOBLES:
                        await self.procesar_debug_tres_dobles(websocket)
                
                except json.JSONDecodeError as e:
                    logger.error(f"Error parseando JSON de {addr}: {e} - mensaje: {mensaje_str[:100]}")
                    await self.enviar(websocket, proto.mensaje_error("Mensaje JSON inválido"))
                except Exception as e:
                    logger.error(f"Error procesando mensaje de {addr}: {e}", exc_info=True)
                    # No romper el loop, seguir escuchando
        
        except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"Cliente {addr} ({nombre}) cerró conexión normalmente")
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"Cliente {addr} ({nombre}) cerró conexión con error: {e.code} - {e.reason}")
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Cliente {addr} ({nombre}) desconectado: {e.code} - {e.reason}")
        except asyncio.CancelledError:
            logger.info(f"Tarea cancelada para {addr} ({nombre})")
            raise  # Re-raise para permitir limpieza apropiada
        except Exception as e:
            logger.error(f"Error inesperado en manejar_cliente para {addr}: {e}", exc_info=True)
        finally:
            logger.debug(f"Limpiando cliente {nombre} ({addr})")
            
            # Asegurar que se remueve de clientes activos
            self.clientes_activos.discard(websocket)
            
            # Limpiar del game_manager
            await self.limpiar_cliente(websocket, nombre)
    
    async def limpiar_cliente(self, websocket, nombre):
        """Limpia los recursos de un cliente desconectado"""
        try:
            try:
                self.clientes_activos.discard(websocket)
            except Exception:
                pass

            nombre_real, color, admin_promoted = self.game_manager.eliminar_jugador(websocket)

            if nombre_real:
                logger.info(f"{nombre_real} ({color}) desconectado")
                try:
                    msg_desc = proto.crear_mensaje(proto.MSG_JUGADOR_DESCONECTADO, nombre=nombre_real, color=color)
                    await self.broadcast(msg_desc)
                except Exception:
                    logger.exception("Error enviando MSG_JUGADOR_DESCONECTADO en broadcast")

            if admin_promoted:
                try:
                    nuevo_sock = admin_promoted.get("socket")
                    nuevo_nombre = admin_promoted.get("nombre", "Administrador")
                    
                    try:
                        await self.enviar(nuevo_sock, proto.mensaje_info(
                            "Has sido promovido a administrador. Para iniciar la partida envía MSG_LISTO.",
                            es_admin=True
                        ))
                        logger.info(f"Notificado PRIVADAMENTE a nuevo admin: {nuevo_nombre}")
                    except Exception:
                        logger.exception("Error enviando mensaje privado al nuevo admin")

                    try:
                        await self.broadcast(proto.mensaje_info(f"El administrador actual es: {nuevo_nombre}"))
                    except Exception:
                        logger.exception("Error haciendo broadcast del nuevo administrador")
                except Exception:
                    logger.exception("Error procesando admin_promoted en limpiar_cliente")
            
            try:
                naveg = len(self.game_manager.jugadores)
                jugadores_lista = self.game_manager.obtener_info_jugadores()
                await self.broadcast(proto.mensaje_esperando(naveg, proto.MIN_JUGADORES, jugadores_lista))
            except Exception:
                logger.exception("Error enviando MSG_ESPERANDO tras desconexión")

            try:
                if (self.game_manager.juego_iniciado and
                        not getattr(self.game_manager, 'juego_terminado', False)):
                    self.game_manager.manejar_desconexion_en_turno(websocket)
                    await asyncio.sleep(0.1)
                    try:
                        await self.notificar_turno()
                    except Exception:
                        logger.exception("Error notificando turno tras desconexión")
            except Exception:
                logger.exception("Error al manejar desconexión durante partida")

            try:
                await websocket.close()
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error limpiando cliente: {e}")

    # ========== MÉTODOS DE AUTENTICACIÓN ==========
    
    async def enviar_directo(self, websocket, mensaje):
        """Envía un mensaje directamente sin verificar clientes_activos (para auth)"""
        try:
            mensaje_json = json.dumps(mensaje, ensure_ascii=False)
            logger.debug(f"Enviando directo a {websocket.remote_address}: {mensaje}")
            await websocket.send(mensaje_json)
            logger.debug(f"Mensaje enviado exitosamente")
        except websockets.exceptions.ConnectionClosed:
            logger.debug("No se pudo enviar: conexión cerrada")
        except Exception as e:
            logger.error(f"Error enviando mensaje directo: {e}")
    
    async def procesar_registro_usuario(self, websocket, mensaje):
        """Procesa el registro de un nuevo usuario"""
        try:
            username = mensaje.get("username")
            password = mensaje.get("password")
            email = mensaje.get("email")
            
            logger.info(f"Intento de registro: usuario={username}")
            
            # Validar datos
            if not username or not password:
                respuesta = proto.mensaje_registro_exitoso(
                    False, 
                    "Usuario y contraseña son obligatorios"
                )
                await self.enviar_directo(websocket, respuesta)
                return
            
            # Intentar registrar en la base de datos
            exito, mensaje_resultado = self.db_manager.registrar_usuario(
                username, password, email
            )
            
            # Enviar respuesta
            respuesta = proto.mensaje_registro_exitoso(exito, mensaje_resultado)
            await self.enviar_directo(websocket, respuesta)
            
            if exito:
                logger.info(f"✅ Usuario registrado exitosamente: {username}")
            else:
                logger.warning(f"❌ Fallo en registro: {mensaje_resultado}")
                
        except Exception as e:
            logger.error(f"Error en procesar_registro_usuario: {e}", exc_info=True)
            respuesta = proto.mensaje_registro_exitoso(False, "Error interno del servidor")
            await self.enviar_directo(websocket, respuesta)
    
    async def procesar_login_usuario(self, websocket, mensaje):
        """Procesa el login de un usuario"""
        try:
            username = mensaje.get("username")
            password = mensaje.get("password")
            
            logger.info(f"Intento de login: usuario={username}")
            
            # Validar datos
            if not username or not password:
                respuesta = proto.mensaje_login_exitoso(
                    False,
                    "Usuario y contraseña son obligatorios",
                    None
                )
                await self.enviar_directo(websocket, respuesta)
                return
            
            # Intentar autenticar
            exito, mensaje_resultado, usuario_id = self.db_manager.autenticar_usuario(
                username, password
            )
            
            # Enviar respuesta
            respuesta = proto.mensaje_login_exitoso(exito, mensaje_resultado, usuario_id)
            await self.enviar_directo(websocket, respuesta)
            
            if exito:
                logger.info(f"✅ Login exitoso: {username} (ID: {usuario_id})")
            else:
                logger.warning(f"❌ Fallo en login: {mensaje_resultado}")
                
        except Exception as e:
            logger.error(f"Error en procesar_login_usuario: {e}", exc_info=True)
            respuesta = proto.mensaje_login_exitoso(False, "Error interno del servidor", None)
            await self.enviar_directo(websocket, respuesta)
    
    async def procesar_obtener_estadisticas(self, websocket, mensaje):
        """Procesa la solicitud de estadísticas de un usuario"""
        try:
            usuario_id = mensaje.get("usuario_id")
            
            logger.info(f"Solicitud de estadísticas: usuario_id={usuario_id}")
            
            # Validar datos
            if not usuario_id:
                respuesta = proto.mensaje_estadisticas(
                    False,
                    "ID de usuario requerido",
                    None
                )
                await self.enviar_directo(websocket, respuesta)
                return
            
            # Obtener estadísticas
            stats = self.db_manager.obtener_estadisticas(usuario_id)
            
            if stats:
                respuesta = proto.mensaje_estadisticas(True, "Estadísticas obtenidas", stats)
                logger.info(f"✅ Estadísticas enviadas para usuario ID: {usuario_id}")
            else:
                respuesta = proto.mensaje_estadisticas(False, "Usuario no encontrado", None)
                logger.warning(f"❌ Usuario no encontrado: {usuario_id}")
            
            await self.enviar_directo(websocket, respuesta)
                
        except Exception as e:
            logger.error(f"Error en procesar_obtener_estadisticas: {e}", exc_info=True)
            respuesta = proto.mensaje_estadisticas(False, "Error interno del servidor", None)
            await self.enviar_directo(websocket, respuesta)
    
    # ========== FIN MÉTODOS DE AUTENTICACIÓN ==========

    # ========== MÉTODOS DE ESTADÍSTICAS ==========
    
    async def registrar_fin_partida(self, websocket_ganador):
        """
        Registra el fin de partida en la base de datos.
        - El ganador recibe VICTORIA
        - Los demás jugadores reciben DERROTA
        """
        try:
            info_ganador = self.game_manager.clientes.get(websocket_ganador)
            if not info_ganador:
                logger.warning("⚠️ No se encontró info del ganador para registrar estadísticas")
                return
            
            jugadores_totales = len(self.game_manager.clientes)
            
            # Registrar para cada jugador
            for ws, info in self.game_manager.clientes.items():
                usuario_id = info.get("usuario_id")
                
                if not usuario_id:
                    logger.debug(f"⏭️ Jugador {info['nombre']} no tiene usuario_id (invitado), omitiendo registro")
                    continue
                
                # Determinar resultado
                es_ganador = ws == websocket_ganador
                resultado = "VICTORIA" if es_ganador else "DERROTA"
                
                # Contar fichas en meta del jugador
                jugador = info.get("jugador")
                fichas_meta = 0
                if jugador:
                    fichas_meta = sum(1 for f in jugador.fichas if f.estado == proto.ESTADO_META)
                
                # Registrar en base de datos
                exito = self.db_manager.registrar_partida(
                    usuario_id=usuario_id,
                    resultado=resultado,
                    color=info["color"],
                    fichas_meta=fichas_meta,
                    turnos=0,  # TODO: Implementar contador de turnos si es necesario
                    tiempo=0,  # TODO: Implementar tiempo de juego si es necesario
                    jugadores=jugadores_totales
                )
                
                if exito:
                    logger.info(f"✅ Estadísticas registradas para {info['nombre']}: {resultado}")
                else:
                    logger.warning(f"❌ Error registrando estadísticas para {info['nombre']}")
                    
        except Exception as e:
            logger.error(f"❌ Error en registrar_fin_partida: {e}", exc_info=True)
    
    # ========== FIN MÉTODOS DE ESTADÍSTICAS ==========

    async def procesar_mensaje(self, websocket, mensaje):
        """Procesa los diferentes tipos de mensajes del cliente"""
        try:
            tipo = mensaje.get("tipo")
            cliente_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            logger.debug(f"Procesando {tipo} de {cliente_info}")

            if tipo == proto.MSG_SYNC_REQUEST:
                logger.debug(f"SYNC_REQUEST recibido de {cliente_info}")
                
                # T1: Timestamp del cliente (recibido en el mensaje)
                t1 = mensaje.get("t1")
                
                # T2: Timestamp cuando el servidor recibió el mensaje
                t2 = time.time()
                
                # T3: Timestamp cuando el servidor envía la respuesta
                t3 = time.time()
                
                # Enviar respuesta inmediatamente
                respuesta = proto.mensaje_sync_response(t1, t2, t3)
                await self.enviar(websocket, respuesta)
                
                logger.debug(f"SYNC_RESPONSE enviado: T1={t1:.6f}, T2={t2:.6f}, T3={t3:.6f}")
                return

            # 🆕 ============ NUEVO BLOQUE: Manejar solicitud de colores ============
            if tipo == proto.MSG_SOLICITAR_COLORES:
                logger.info(f"Solicitud de colores disponibles de {cliente_info}")
                colores = self.game_manager.obtener_colores_disponibles()
                await self.enviar(websocket, proto.mensaje_colores_disponibles(colores))
                return
            # 🆕 ============ FIN DEL NUEVO BLOQUE ============

            if tipo == proto.MSG_LISTO:
                logger.info(f"MSG_LISTO recibido de {cliente_info}")

                admin_sock = getattr(self.game_manager, "admin_cliente", None)

                if websocket != admin_sock:
                    logger.warning(f"Intento de iniciar partida por no-admin: {cliente_info}")
                    await self.enviar(websocket, proto.mensaje_error("Sólo el administrador puede iniciar la partida"))
                    return

                if len(self.game_manager.jugadores) < proto.MIN_JUGADORES:
                    await self.enviar(websocket, proto.mensaje_error(
                        f"No hay suficientes jugadores (mínimo {proto.MIN_JUGADORES})"
                    ))
                    return

                if getattr(self.game_manager, "juego_iniciado", False):
                    await self.enviar(websocket, proto.mensaje_info("El juego ya está iniciado"))
                    return

                # ⭐ NUEVO: Iniciar fase de determinación de turnos en lugar del juego directo
                logger.info("Administrador autorizado. Iniciando fase de determinación de turnos...")
                await self.iniciar_determinacion()
                return
            
            # ⭐ NUEVO: Handler para tiradas durante la determinación
            if tipo == proto.MSG_DETERMINACION_TIRADA:
                logger.info(f"MSG_DETERMINACION_TIRADA recibido de {cliente_info}")
                await self.procesar_tirada_determinacion(websocket, mensaje)
                return

            if tipo == proto.MSG_LANZAR_DADOS:
                logger.info(f"LANZAR_DADOS recibido de {cliente_info}")
                await self.procesar_lanzar_dados(websocket)

            elif tipo == proto.MSG_SACAR_CARCEL:
                logger.info(f"SACAR_CARCEL recibido de {cliente_info}")
                await self.procesar_sacar_carcel(websocket)

            elif tipo == proto.MSG_MOVER_FICHA:
                ficha_id = mensaje.get("ficha_id", 0)
                dado_elegido = mensaje.get("dado_elegido", 0)
                logger.info(f"MOVER_FICHA recibido de {cliente_info}, ficha: {ficha_id}, dado: {dado_elegido}")
                await self.procesar_mover_ficha(websocket, ficha_id, dado_elegido)

            elif mensaje.get("tipo") == proto.MSG_SACAR_TODAS:
                if not self.game_manager.es_turno_de(websocket):
                    await self.enviar(websocket, proto.mensaje_error("No es tu turno"))
                    return

                exito, resultado = self.game_manager.sacar_todas_fichas_carcel(websocket)
                if exito:
                    color = self.game_manager.clientes[websocket]["color"]
                    nombre = self.game_manager.clientes[websocket]["nombre"]
                    
                    for ficha_id in resultado["fichas_liberadas"]:
                        await self.broadcast(proto.mensaje_movimiento_ok(
                            nombre=nombre,
                            color=color,
                            ficha_id=ficha_id,
                            desde=-1,
                            hasta=resultado["posicion"],
                            accion="liberar_ficha"
                        ))
                    
                    # ⭐ NUEVO: Notificar capturas si hubo
                    if "capturas" in resultado and resultado["capturas"]:
                        for captura in resultado["capturas"]:
                            await self.broadcast(proto.crear_mensaje(
                                proto.MSG_CAPTURA,
                                capturado={
                                    "nombre": captura["nombre"],
                                    "color": captura["color"],
                                    "ficha_id": captura["ficha_id"]
                                }
                            ))
                            logger.info(f"🍽️ {nombre} ({color}) capturó ficha de "
                                       f"{captura['nombre']} ({captura['color']}) al liberar todas las fichas")
                    
                    await self.broadcast(proto.mensaje_tablero(self.game_manager.obtener_estado_tablero()))
                    
                    if self.game_manager.debe_avanzar_turno_ahora():
                        self.game_manager.avanzar_turno()
                        await self.notificar_turno()
                else:
                    await self.enviar(websocket, proto.mensaje_error(resultado))
                    return

            # ⭐ NUEVO: Handler para debug de 3 dobles
            elif tipo == proto.MSG_DEBUG_FORZAR_TRES_DOBLES:
                await self.procesar_debug_tres_dobles(websocket)
                return
            
            # ⭐ NUEVO: Handler para elegir ficha del premio
            elif tipo == proto.MSG_ELEGIR_FICHA_PREMIO:
                await self.procesar_elegir_ficha_premio(websocket, mensaje)
                return
            
            else:
                logger.warning(f"Mensaje no reconocido de {cliente_info}: {tipo}")
                await self.enviar(websocket, proto.mensaje_error("Mensaje no reconocido"))

        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            try:
                await self.enviar(websocket, proto.mensaje_error("Error interno del servidor"))
            except Exception:
                logger.exception("Fallo al enviar mensaje de error al cliente")

    async def procesar_lanzar_dados(self, websocket):
        """Procesa el lanzamiento de dados"""
        cliente_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"INICIANDO procesamiento de dados para {cliente_info}")
    
        try:
            es_turno = self.game_manager.es_turno_de(websocket)
            if not es_turno:
                error_msg = "No es tu turno"
                logger.warning(f"{error_msg} para {cliente_info}")
                await self.enviar(websocket, proto.mensaje_error(error_msg))
                return
        
            dado1, dado2, suma, es_doble = self.game_manager.lanzar_dados_safe()
            logger.info(f"Dados generados: [{dado1}] [{dado2}] = {suma}, dobles: {es_doble}")
        
            mensaje_dados = proto.mensaje_dados(dado1, dado2, suma, es_doble)
            await self.broadcast(mensaje_dados)
            logger.info(f"Dados enviados exitosamente")
        
            # ⭐ CRÍTICO: Verificar PRIMERO si se activó el premio de 3 dobles
            if self.game_manager.premio_tres_dobles:
                logger.info(f"🏆 Premio de 3 dobles activado - solicitando elección de ficha...")
                
                info = self.game_manager.clientes[websocket]
                
                # Obtener fichas elegibles
                fichas_elegibles = self.game_manager.obtener_fichas_elegibles_para_premio(websocket)
                
                if fichas_elegibles:
                    # Enviar mensaje al jugador para que elija
                    await self.enviar(websocket, proto.mensaje_premio_tres_dobles(info['nombre'], fichas_elegibles))
                    logger.info(f"Mensaje de premio enviado a {info['nombre']} con {len(fichas_elegibles)} fichas elegibles")
                else:
                    logger.warning(f"{info['nombre']} no tiene fichas elegibles para el premio")
                    await self.broadcast(proto.mensaje_info(
                        f"{info['nombre']} sacó 3 dobles pero no tiene fichas elegibles. Turno pasado."
                    ))
                    # Avanzar turno automáticamente
                    self.game_manager.premio_tres_dobles = False
                    self.game_manager.dobles_consecutivos = 0
                    self.game_manager.ultimo_es_doble = False
                    if self.game_manager.avanzar_turno():
                        await self.broadcast_tablero()
                        await self.notificar_turno()
                
                logger.info(f"COMPLETADO: Dados [{dado1}] [{dado2}] = {suma} (¡PREMIO DE 3 DOBLES!)")
                return
            
            # Si hay dobles pero NO es premio, intentar sacar fichas de la cárcel
            if es_doble:
                logger.info(f"Dobles detectados - liberando TODAS las fichas automáticamente...")
                
                # ⭐ DELAY para que el cliente procese los dados antes de las acciones
                await asyncio.sleep(0.5)
            
                exito, resultado = self.game_manager.sacar_todas_fichas_carcel(websocket)
            
                if exito:
                    info = self.game_manager.clientes[websocket]
                    fichas_liberadas = resultado.get("fichas_liberadas", [])
                
                    for ficha_id in fichas_liberadas:
                        await self.broadcast(proto.crear_mensaje(
                            proto.MSG_MOVIMIENTO_OK,
                            nombre=info["nombre"],
                            color=info["color"],
                            ficha_id=ficha_id,
                            desde=-1,
                            hasta=resultado.get("posicion", 0),
                            accion="liberar_ficha"
                        ))
                        await asyncio.sleep(0.05)  # Pequeño delay entre cada ficha
                
                    logger.info(f"{len(fichas_liberadas)} fichas liberadas para {info['nombre']}")
                    
                    # ⭐ DELAY antes de enviar el tablero actualizado
                    await asyncio.sleep(0.3)
                    await self.broadcast_tablero()
                
                    await self.broadcast(proto.crear_mensaje(
                        proto.MSG_INFO,
                        mensaje=f"¡{info['nombre']} sacó dobles! Todas las fichas liberadas. Mantiene el turno."
                    ))
                    
                    logger.info(f"{info['nombre']} mantiene el turno - reenviando notificación")
                    await asyncio.sleep(0.2)
                    await self.broadcast(proto.mensaje_turno(info["nombre"], info["color"]))
                
                # ⭐ NUEVO: Verificar si puede hacer alguna acción CON DOBLES después de sacar/no tener fichas en cárcel
                if not self.game_manager.puede_hacer_alguna_accion(websocket):
                    info = self.game_manager.clientes[websocket]
                    logger.info(f"{info['nombre']} sacó dobles pero no puede mover ninguna ficha - pasando turno")
                    
                    await self.broadcast(proto.crear_mensaje(
                        proto.MSG_INFO,
                        mensaje=f"{info['nombre']} sacó dobles pero no puede hacer ninguna acción. Turno pasado."
                    ))
                    
                    if self.game_manager.forzar_avance_turno():
                        logger.info("Turno forzado - notificando al siguiente jugador")
                        await asyncio.sleep(0.2)
                        await self.broadcast_tablero()
                        await asyncio.sleep(0.1)
                        await self.notificar_turno()
            
            else:
                logger.info(f"Sin dobles - verificando si puede hacer acciones...")
            
                if self.game_manager.necesita_pasar_turno_automaticamente(websocket):
                    info = self.game_manager.clientes[websocket]
                
                    logger.info(f"{info['nombre']} no puede hacer ninguna acción - pasando turno automáticamente")
                
                    await self.broadcast(proto.crear_mensaje(
                        proto.MSG_INFO,
                        mensaje=f"{info['nombre']} no puede hacer ninguna acción. Turno pasado automáticamente."
                    ))
                
                    if self.game_manager.forzar_avance_turno():
                        logger.info("Turno forzado - notificando al siguiente jugador")
                        await asyncio.sleep(0.2)
                        await self.broadcast_tablero()
                        await asyncio.sleep(0.1)
                        await self.notificar_turno()
                        logger.info("Notificación de turno enviada al siguiente jugador")
                    return
                else:
                    logger.info(f"Jugador puede mover fichas - esperando acción")
        
            logger.info(f"COMPLETADO: Dados [{dado1}] [{dado2}] = {suma} {'(DOBLES!)' if es_doble else ''}")
        
        except Exception as e:
            logger.error(f"ERROR CRÍTICO en procesamiento de dados: {e}")
            await self.enviar(websocket, proto.mensaje_error("Error generando dados"))

    async def procesar_sacar_carcel(self, websocket):
        """Procesa el intento de sacar una ficha de la cárcel"""
        exito, resultado = self.game_manager.sacar_de_carcel(websocket)
        
        if not exito:
            logger.warning(f"Error sacando de cárcel: {resultado}")
            await self.enviar(websocket, proto.mensaje_error(resultado))
            return
        
        info = self.game_manager.clientes[websocket]
        color = info["color"]
        salida = self.game_manager.tablero.salidas[color]  # Usar diccionario directo
        
        await self.broadcast(proto.crear_mensaje(
            proto.MSG_MOVIMIENTO_OK,
            nombre=info["nombre"],
            color=color,
            ficha_id=resultado.get("ficha_id", 0),
            desde=-1,
            hasta=salida
        ))
        
        # ⭐ NUEVO: Notificar capturas si hubo
        if "capturas" in resultado and resultado["capturas"]:
            for captura in resultado["capturas"]:
                await self.broadcast(proto.crear_mensaje(
                    proto.MSG_CAPTURA,
                    capturado={
                        "nombre": captura["nombre"],
                        "color": captura["color"],
                        "ficha_id": captura["ficha_id"]
                    }
                ))
                logger.info(f"🍽️ {info['nombre']} ({color}) capturó ficha de "
                           f"{captura['nombre']} ({captura['color']}) al salir de cárcel")
        
        logger.info(f"{info['nombre']} sacó ficha de la cárcel")
        await self.broadcast_tablero()
        
        if self.game_manager.debe_avanzar_turno_ahora():
            turno_avanzado = self.game_manager.avanzar_turno()
            if turno_avanzado:
                await asyncio.sleep(0.1)
                await self.notificar_turno()
            else:
                logger.info("Jugador mantiene turno después de sacar de cárcel")
                await asyncio.sleep(0.1)
                await self.broadcast(proto.mensaje_turno(info["nombre"], info["color"]))
    
    async def procesar_mover_ficha(self, websocket, ficha_id, dado_elegido):
        """Procesa el movimiento de una ficha con el dado elegido"""
        logger.debug(f"Procesando movimiento de ficha {ficha_id} con dado {dado_elegido}")
        
        exito, resultado = self.game_manager.mover_ficha(websocket, ficha_id, dado_elegido)
        
        if not exito:
            logger.warning(f"Error moviendo ficha: {resultado}")
            await self.enviar(websocket, proto.mensaje_error(resultado))
            # ⭐ CRÍTICO: NO avanzar turno ni resetear nada si el movimiento falló
            return
        
        info = self.game_manager.clientes[websocket]
        
        await self.broadcast(proto.crear_mensaje(
            proto.MSG_MOVIMIENTO_OK,
            nombre=info["nombre"],
            color=info["color"],
            ficha_id=ficha_id,
            desde=resultado["desde"],
            hasta=resultado["hasta"]
        ))
        
        # ⭐ NUEVO: Notificar capturas si hubo
        if "capturas" in resultado and resultado["capturas"]:
            for captura in resultado["capturas"]:
                await self.broadcast(proto.crear_mensaje(
                    proto.MSG_CAPTURA,
                    capturado={
                        "nombre": captura["nombre"],
                        "color": captura["color"],
                        "ficha_id": captura["ficha_id"]
                    }
                ))
                logger.info(f"🍽️ {info['nombre']} ({info['color']}) capturó ficha de "
                           f"{captura['nombre']} ({captura['color']})")
        
        logger.info(f"🎮 {info['nombre']} movió ficha {ficha_id}")
        await self.broadcast_tablero()
        
        if self.game_manager.verificar_victoria(websocket):
            await self.broadcast(proto.mensaje_victoria(info["nombre"], info["color"]))
            logger.info(f"¡{info['nombre']} ({info['color']}) HA GANADO!")
            # 🆕 Registrar estadísticas de la partida
            await self.registrar_fin_partida(websocket)
            self.game_manager.juego_terminado = True
            return
        
        if self.game_manager.debe_avanzar_turno_ahora():
            turno_avanzado = self.game_manager.avanzar_turno()
            if turno_avanzado:
                logger.info("Turno avanzado después de mover ficha")
                await asyncio.sleep(0.1)
                await self.notificar_turno()
            else:
                logger.info("Jugador mantiene turno - puede lanzar dados nuevamente")
                await asyncio.sleep(0.1)
                await self.broadcast(proto.mensaje_turno(info["nombre"], info["color"]))
    
    # ============================================
    # MÉTODOS DE DETERMINACIÓN DE TURNOS
    # ============================================
    
    async def iniciar_determinacion(self):
        """Inicia la fase de determinación de turnos"""
        try:
            exito = self.game_manager.iniciar_determinacion_turnos()
            
            if not exito:
                logger.error("No se pudo iniciar la determinación de turnos")
                await self.broadcast(proto.mensaje_error("No se pudo iniciar la determinación"))
                return
            
            # Determinar el primer jugador (ID 0)
            primer_jugador = None
            for ws, info in self.game_manager.clientes.items():
                if info['id'] == 0:
                    primer_jugador = info['nombre']
                    break
            
            # Notificar a todos los jugadores que deben lanzar dados
            logger.info("📢 Enviando MSG_DETERMINACION_INICIO a todos los jugadores")
            logger.info(f"👤 Primer jugador: {primer_jugador}")
            await self.broadcast(proto.mensaje_determinacion_inicio(primer_jugador))
            
            logger.info("✅ Fase de determinación iniciada correctamente")
            
        except Exception as e:
            logger.error(f"Error iniciando determinación: {e}", exc_info=True)
            await self.broadcast(proto.mensaje_error("Error iniciando la fase de determinación"))
    
    async def procesar_tirada_determinacion(self, websocket, mensaje):
        """Procesa una tirada durante la fase de determinación"""
        try:
            dado1 = mensaje.get("dado1")
            dado2 = mensaje.get("dado2")
            
            if dado1 is None or dado2 is None:
                await self.enviar(websocket, proto.mensaje_error("Faltan valores de dados"))
                return
            
            # Validar que los dados sean válidos
            try:
                dado1 = int(dado1)
                dado2 = int(dado2)
                if not (1 <= dado1 <= 6 and 1 <= dado2 <= 6):
                    raise ValueError("Valores fuera de rango")
            except (ValueError, TypeError):
                await self.enviar(websocket, proto.mensaje_error("Valores de dados inválidos"))
                return
            
            info = self.game_manager.clientes.get(websocket)
            if not info:
                await self.enviar(websocket, proto.mensaje_error("Cliente no válido"))
                return
            
            logger.info(f"🎲 Procesando tirada de {info['nombre']}: [{dado1}][{dado2}]")
            
            # Registrar la tirada
            fase_completa, resultado = self.game_manager.registrar_tirada_determinacion(
                websocket, dado1, dado2
            )
            
            # Verificar si hubo error
            if "error" in resultado:
                await self.enviar(websocket, proto.mensaje_error(resultado["error"]))
                return
            
            # Notificar a todos el resultado de esta tirada
            suma = dado1 + dado2
            siguiente_nombre = resultado.get("siguiente", "")
            
            await self.broadcast(proto.mensaje_determinacion_resultado(
                info['nombre'],
                info['color'],
                dado1,
                dado2,
                suma,
                siguiente_nombre
            ))
            
            # Si la fase NO está completa, solo esperamos más tiradas
            if not fase_completa:
                if "pendientes" in resultado:
                    logger.info(f"⏳ Esperando {resultado['pendientes']} jugadores más")
                elif "empate" in resultado:
                    # Hay empate, notificar desempate
                    jugadores_empatados = resultado["jugadores"]
                    valor_empate = resultado["valor"]
                    
                    logger.info(f"⚔️ Empate detectado: {valor_empate} puntos")
                    logger.info(f"⚔️ Jugadores empatados: {[j['nombre'] for j in jugadores_empatados]}")
                    
                    await self.broadcast(proto.mensaje_determinacion_empate(
                        jugadores_empatados,
                        valor_empate
                    ))
                return
            
            # Fase completa: hay un ganador
            if "ganador" in resultado and "orden" in resultado:
                ganador = resultado["ganador"]
                orden = resultado["orden"]
                
                logger.info(f"🏆 GANADOR: {ganador['nombre']} ({ganador['color']})")
                logger.info(f"📋 ORDEN: {' -> '.join([j['nombre'] for j in orden])}")
                
                # Notificar ganador y orden
                await self.broadcast(proto.mensaje_determinacion_ganador(
                    ganador['nombre'],
                    ganador['color'],
                    orden
                ))
                
                # Pequeña pausa para que los clientes procesen
                await asyncio.sleep(1.0)
                
                # Ahora SÍ iniciar el juego normal
                logger.info("🎮 Iniciando juego normal con orden determinado...")
                await self.iniciar_juego()
            
        except Exception as e:
            logger.error(f"Error procesando tirada de determinación: {e}", exc_info=True)
            await self.enviar(websocket, proto.mensaje_error("Error procesando tirada"))
    
    # ============================================
    # FIN MÉTODOS DE DETERMINACIÓN DE TURNOS
    # ============================================
    
    async def iniciar_juego(self):
        """Inicia el juego"""
        logger.info("Iniciando juego...")
        
        self.game_manager.iniciar_juego()
        jugadores_info = self.game_manager.obtener_info_jugadores()
        
        await self.broadcast(proto.crear_mensaje(
            proto.MSG_INICIO_JUEGO,
            jugadores=jugadores_info
        ))
        
        await self.broadcast_tablero()
        await asyncio.sleep(0.1)
        await self.notificar_turno()
        
        logger.info("Juego iniciado exitosamente")
    
    async def notificar_turno(self):
        """Notifica el turno actual a todos los clientes"""
        jugador_actual = self.game_manager.obtener_jugador_actual_safe()
        if not jugador_actual:
            logger.warning("No se pudo obtener jugador actual")
            return
        
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
        
        mensaje_turno = proto.mensaje_turno(info_encontrada["nombre"], info_encontrada["color"])
        
        logger.info(f"NOTIFICANDO TURNO: {info_encontrada['nombre']} ({info_encontrada['color']})")
        logger.debug(f"Mensaje turno: {mensaje_turno}")
        
        await self.broadcast(mensaje_turno)
        logger.info(f"Notificación de turno enviada a todos los clientes")
    
    async def broadcast_tablero(self):
        """Envía el estado del tablero a todos los clientes"""
        try:
            estado = self.game_manager.obtener_estado_tablero()
            mensaje_tablero = proto.crear_mensaje(proto.MSG_TABLERO, **estado)
            await self.broadcast(mensaje_tablero)
            logger.debug("Estado del tablero enviado")
        except Exception as e:
            logger.error(f"Error enviando estado del tablero: {e}")
    
    async def enviar(self, websocket, mensaje):
        """Envía un mensaje a un cliente específico"""
        try:
            if websocket in self.clientes_activos:
                mensaje_json = json.dumps(mensaje, ensure_ascii=False)
                logger.debug(f"Enviando a {websocket.remote_address}: {mensaje}")
                await websocket.send(mensaje_json)
                logger.debug(f"Mensaje enviado exitosamente")
            else:
                logger.warning(f"Intento de enviar a cliente inactivo")
        except websockets.exceptions.ConnectionClosed:
            logger.debug("No se pudo enviar: conexión cerrada")
            self.clientes_activos.discard(websocket)
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            self.clientes_activos.discard(websocket)
    
    async def broadcast(self, mensaje, excluir=None):
        """Envía un mensaje a todos los clientes conectados"""
        # ⭐ CRÍTICO: Usar clientes_activos en lugar de game_manager.clientes
        # para asegurar que solo enviamos a conexiones válidas
        clientes_a_enviar = list(self.clientes_activos)
        logger.debug(f"BROADCAST a {len(clientes_a_enviar)} clientes activos: {mensaje.get('tipo', mensaje)}")
        
        if not clientes_a_enviar:
            logger.warning("No hay clientes activos para broadcast")
            return
        
        clientes_desconectados = []
        enviados_exitosos = 0
        
        for websocket in clientes_a_enviar:
            if websocket != excluir:
                try:
                    # Enviar directamente sin verificar clientes_activos de nuevo
                    mensaje_json = json.dumps(mensaje, ensure_ascii=False)
                    await websocket.send(mensaje_json)
                    enviados_exitosos += 1
                    logger.debug(f"✅ Broadcast enviado a {websocket.remote_address}")
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"❌ Cliente desconectado durante broadcast: {websocket.remote_address}")
                    clientes_desconectados.append(websocket)
                except Exception as e:
                    logger.error(f"Error en broadcast a {websocket.remote_address}: {e}")
                    clientes_desconectados.append(websocket)
        
        logger.info(f"📡 Broadcast completado: {enviados_exitosos}/{len(clientes_a_enviar)} enviados")
        
        for websocket in clientes_desconectados:
            self.clientes_activos.discard(websocket)
            if websocket in self.game_manager.clientes:
                nombre = self.game_manager.clientes[websocket].get("nombre", "Desconocido")
                await self.limpiar_cliente(websocket, nombre)
        
    async def procesar_elegir_ficha_premio(self, websocket, mensaje):
        """Procesa la elección de ficha para el premio de 3 dobles"""
        try:
            info = self.game_manager.clientes.get(websocket)
            
            if not info:
                await self.enviar(websocket, proto.mensaje_error("Cliente no válido"))
                return
            
            ficha_id = mensaje.get("ficha_id")
            if ficha_id is None or ficha_id < 0:
                # Cliente envió -1 indicando error de input (ValueError)
                if ficha_id == -1:
                    await self.enviar(websocket, proto.mensaje_error("Entrada inválida, por favor ingresa un número"))
                else:
                    await self.enviar(websocket, proto.mensaje_error("ID de ficha no especificado"))
                
                # Reenviar mensaje de premio para retry
                fichas_elegibles = self.game_manager.obtener_fichas_elegibles_para_premio(websocket)
                if fichas_elegibles:
                    await self.enviar(websocket, proto.mensaje_premio_tres_dobles(info['nombre'], fichas_elegibles))
                return
            
            logger.info(f"🏆 {info['nombre']} eligió la ficha {ficha_id} para enviar a META")
            
            # Aplicar el premio
            exito, resultado = self.game_manager.aplicar_premio_tres_dobles(websocket, ficha_id)
            
            if not exito:
                error_msg = resultado.get("error", "Error aplicando premio")
                logger.warning(f"❌ Elección inválida de {info['nombre']}: {error_msg}")
                await self.enviar(websocket, proto.mensaje_error(error_msg))
                
                # ⭐ CRÍTICO: Reenviar mensaje de premio para que pueda reintentar
                fichas_elegibles = self.game_manager.obtener_fichas_elegibles_para_premio(websocket)
                if fichas_elegibles:
                    await self.enviar(websocket, proto.mensaje_premio_tres_dobles(info['nombre'], fichas_elegibles))
                    logger.info(f"🔄 Reenviado mensaje de premio a {info['nombre']} para retry")
                return
            
            # Notificar a todos el premio aplicado
            await self.broadcast(proto.crear_mensaje(
                proto.MSG_INFO,
                mensaje=f"🏆 {info['nombre']} envió su ficha #{ficha_id + 1} directamente a META con el premio de 3 dobles!"
            ))
            
            # Actualizar tablero
            await self.broadcast_tablero()
            
            # Verificar si ganó
            if resultado.get("ha_ganado"):
                await self.broadcast(proto.mensaje_victoria(info["nombre"], info["color"]))
                logger.info(f"🎊 ¡{info['nombre']} ha ganado con el premio de 3 dobles!")
                # 🆕 Registrar estadísticas de la partida
                await self.registrar_fin_partida(websocket)
                return
            
            # Avanzar turno
            if self.game_manager.avanzar_turno():
                await self.broadcast_tablero()
                await self.notificar_turno()
            
        except Exception as e:
            logger.error(f"Error en procesar_elegir_ficha_premio: {e}", exc_info=True)
            await self.enviar(websocket, proto.mensaje_error("Error procesando elección de ficha"))
    
    async def procesar_debug_tres_dobles(self, websocket):
        """🔧 DEBUG: Procesa comando para forzar 3 dobles consecutivos"""
        try:
            info = self.game_manager.clientes.get(websocket)
            
            if not info:
                await self.enviar(websocket, proto.mensaje_error("Cliente no válido"))
                return
            
            exito, resultado = self.game_manager.forzar_tres_dobles_debug(websocket)
            
            if not exito:
                await self.enviar(websocket, proto.mensaje_error(resultado))
                return
            
            logger.warning(f"🔧 DEBUG: {info['nombre']} forzó 3 dobles consecutivos")
            
            # Notificar a todos sobre los dados
            await self.broadcast(proto.crear_mensaje(
                proto.MSG_DADOS,
                dado1=resultado['dado1'],
                dado2=resultado['dado2'],
                suma=resultado['suma'],
                es_doble=True,
                dobles_consecutivos=resultado['dobles_consecutivos']
            ))
            
            # Notificar premio
            await self.broadcast(proto.crear_mensaje(
                proto.MSG_INFO,
                mensaje=f"🏆 ¡{info['nombre'].upper()} sacó 3 dobles consecutivos! Puede enviar UNA ficha a META."
            ))
            
            # Obtener fichas elegibles
            try:
                fichas_elegibles = self.game_manager.obtener_fichas_elegibles_para_premio(websocket)
                
                if not fichas_elegibles:
                    await self.broadcast(proto.crear_mensaje(
                        proto.MSG_INFO,
                        mensaje=f"{info['nombre']} no tiene fichas elegibles para el premio (todas en cárcel o meta)."
                    ))
                    # Forzar avance de turno
                    if self.game_manager.avanzar_turno():
                        await self.broadcast_tablero()
                        await self.notificar_turno()
                    return
                
                # Notificar al jugador que debe elegir
                await self.enviar(websocket, proto.crear_mensaje(
                    proto.MSG_PREMIO_TRES_DOBLES,
                    fichas_elegibles=fichas_elegibles,
                    mensaje="Elige una ficha para enviar a META"
                ))
                
                logger.info(f"✅ Jugador {info['nombre']} tiene {len(fichas_elegibles)} fichas elegibles para premio")
                
            except Exception as e:
                logger.error(f"Error obteniendo fichas elegibles: {e}", exc_info=True)
                await self.enviar(websocket, proto.mensaje_error("Error obteniendo fichas elegibles"))
                
        except Exception as e:
            logger.error(f"Error en procesar_debug_tres_dobles: {e}", exc_info=True)
            await self.enviar(websocket, proto.mensaje_error("Error interno del servidor"))
    
    def detener(self):
        """Detiene el servidor"""
        logger.info("🛑 Deteniendo servidor...")
        self.running = False
        logger.info("✅ Servidor detenido")


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8001
    
    servidor = ParchisServer(HOST, PORT)
    
    try:
        asyncio.run(servidor.iniciar())
    except KeyboardInterrupt:
        logger.info("Interrupción recibida...")
        servidor.detener()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        servidor.detener()