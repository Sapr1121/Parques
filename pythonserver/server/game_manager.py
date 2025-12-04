import random
import threading
import logging
from parchis import Table
from user import User
import gameFile as tkn
import protocol as proto

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.tablero = Table()
        self.jugadores = []
        self.clientes = {}
        self.admin_cliente = None
        self.admin_id = None
        self.turno_actual = 0
        self.juego_iniciado = False
        self.juego_terminado = False
        self.lock = threading.RLock()
        
        # Nuevo: ID monotónico para jugadores
        self.next_player_id = 0

        # Estado de los últimos dados lanzados
        self.ultimo_dado1 = 0
        self.ultimo_dado2 = 0
        self.ultima_suma = 0
        self.ultimo_es_doble = False
        self.dados_lanzados = False
        
        # Control de dobles consecutivos
        self.dobles_consecutivos = 0
        self.max_dobles = 3
        self.premio_tres_dobles = False  # ⭐ NUEVO: Flag para premio de 3 dobles
        
        # Control de estado de turno
        self.accion_realizada = False
        self.debe_avanzar_turno = False
        
        # ⭐ NUEVO: Control de determinación de turnos
        self.determinacion_activa = False
        self.tiradas_determinacion = {}  # {websocket: {'nombre', 'color', 'dado1', 'dado2', 'suma'}}
        self.jugadores_en_desempate = set()  # Jugadores que deben tirar en desempate
        self.orden_turnos_determinado = []  # Lista ordenada de jugadores según determinación
    
    def agregar_jugador(self, websocket, nombre, color_elegido=None, usuario_id=None):
        """
        Agrega un jugador al juego.
        Args:
            websocket: conexión del cliente
            nombre: nombre del jugador
            color_elegido: color seleccionado por el jugador (opcional)
            usuario_id: ID del usuario en la base de datos (opcional)
        
        Retorna: (color, error, es_admin, es_host)
        """
        with self.lock:
            logger.debug(f"🔒 Agregando jugador {nombre} con color preferido: {color_elegido} (usuario_id={usuario_id})")

            # Validar límite de jugadores
            if len(self.jugadores) >= proto.MAX_JUGADORES:
                logger.warning("Intento de agregar jugador pero el servidor está lleno")
                return None, "Servidor lleno", False, False

            # Determinar colores disponibles
            colores_usados = [j.color for j in self.jugadores]
            colores_disponibles = [c for c in proto.COLORES if c not in colores_usados]

            if not colores_disponibles:
                logger.warning("No hay colores disponibles al agregar jugador")
                return None, "No hay colores disponibles", False, False

            # Validar color elegido
            if color_elegido:
                if color_elegido not in proto.COLORES:
                    return None, f"Color '{color_elegido}' no válido", False, False
                if color_elegido in colores_usados:
                    return None, f"Color '{color_elegido}' ya está en uso", False, False
                color = color_elegido
            else:
                # Asignación automática si no se especifica color
                color = colores_disponibles[0]

            jugador_id = self.next_player_id
            self.next_player_id += 1

            usuario = User(nombre, color)

            # Crear fichas bloqueadas en la cárcel
            for i in range(proto.FICHAS_POR_JUGADOR):
                ficha = tkn.gameToken(color, proto.ESTADO_BLOQUEADO)
                ficha.id = i
                usuario.agregar_ficha(ficha)

            # Añadir a lista de jugadores y mapping de clientes
            self.jugadores.append(usuario)
            self.clientes[websocket] = {
                "jugador": usuario,
                "nombre": nombre,
                "color": color,
                "id": jugador_id,
                "usuario_id": usuario_id  # 🆕 ID de la base de datos
            }

            # Gestionar admin
            es_admin = False
            if not self.admin_cliente:
                self.admin_cliente = websocket
                self.admin_id = jugador_id
                usuario.es_admin = True
                es_admin = True
                logger.info(f"🔑 {nombre} (ID {jugador_id}) designado como administrador del servidor")
            else:
                usuario.es_admin = False

            # Gestionar host
            es_host = False
            if len(self.jugadores) == 1:
                self.host_cliente = websocket
                self.host_info = {"nombre": nombre, "color": color, "socket": websocket}
                es_host = True
                logger.info(f"🏠 {nombre} es ahora el HOST del juego")

            logger.info(f"✅ Jugador {nombre} agregado como {color} (ID: {jugador_id}, Admin: {es_admin}, Host: {es_host})")
            return color, None, es_admin, es_host
            

    def obtener_colores_disponibles(self):
        """
        Retorna lista de colores que aún no están siendo usados.
        """
        with self.lock:
            colores_usados = [j.color for j in self.jugadores]
            colores_disponibles = [c for c in proto.COLORES if c not in colores_usados]
            logger.debug(f"🎨 Colores disponibles: {colores_disponibles}")
            return colores_disponibles
    
    def eliminar_jugador(self, socket_cliente):
        """
        Elimina el jugador asociado al socket_cliente.
        Si el jugador eliminado era admin, promueve al siguiente jugador
        (el primero en la lista restante) como nuevo admin.
        Retorna: (nombre, color, admin_promoted)
        - nombre, color: del jugador eliminado (o (None, None) si no existía)
        - admin_promoted: dict con keys {'socket','id','nombre','color'} si se promovió a alguien,
                            o None si no hubo promoción (por ejemplo no quedaban jugadores).
        """
        with self.lock:
            logger.debug("🔒 Eliminando jugador")

            if socket_cliente not in self.clientes:
                return None, None, None

            info = self.clientes[socket_cliente]
            jugador = info["jugador"]
            nombre = info.get("nombre")
            color = info.get("color")

            # Ajustar turno actual si es necesario y remover de la lista de jugadores
            try:
                jugador_index = self.jugadores.index(jugador)
                if jugador_index <= self.turno_actual and self.turno_actual > 0:
                    self.turno_actual -= 1
                self.jugadores.remove(jugador)
            except ValueError:
                logger.warning(f"Jugador {nombre} no encontrado en lista de jugadores")

            # Eliminar del mapping de clientes
            try:
                del self.clientes[socket_cliente]
            except KeyError:
                logger.warning(f"Socket {socket_cliente} no encontrado en mapping de clientes al eliminar")

            admin_promoted = None

            # Gestionar cambio de admin si es necesario
            if self.admin_cliente == socket_cliente:
                logger.info(f"El administrador {nombre} se ha desconectado")
                self.admin_cliente = None
                self.admin_id = None

                # Si hay jugadores restantes, promover al primero de la lista
                if self.jugadores:
                    # Primero limpiar flags es_admin en todos los jugadores restantes
                    for p in self.jugadores:
                        try:
                            p.es_admin = False
                        except Exception:
                            # si la estructura del objeto no tiene es_admin, ignorar
                            pass

                    nuevo_admin = self.jugadores[0]
                    # Buscar el socket correspondiente en el mapping de clientes
                    for sock, data in list(self.clientes.items()):
                        if data.get("jugador") is nuevo_admin:
                            self.admin_cliente = sock
                            self.admin_id = data.get("id")
                            try:
                                nuevo_admin.es_admin = True
                            except Exception:
                                pass
                            admin_promoted = {
                                "socket": sock,
                                "id": data.get("id"),
                                "nombre": data.get("nombre"),
                                "color": data.get("color")
                            }
                            logger.info(f"🔑 Nuevo administrador: {data.get('nombre')} (ID: {data.get('id')})")
                            break

                    if not self.admin_cliente:
                        logger.warning("No se pudo asignar nuevo administrador (no se encontró socket correspondiente)")
                else:
                    logger.info("No quedan jugadores, juego sin administrador")

            logger.info(f"✅ Jugador {nombre} ({color}) eliminado")
            return nombre, color, admin_promoted

    
    def manejar_desconexion_en_turno(self, socket_cliente):
        """Maneja cuando se desconecta el jugador que tiene el turno"""
        with self.lock:
            logger.debug("🔒 Manejando desconexión en turno")
            
            if socket_cliente in self.clientes:
                jugador_desconectado = self.clientes[socket_cliente]["jugador"]
                jugador_actual = None
                
                if self.jugadores and not self.juego_terminado:
                    jugador_actual = self.jugadores[self.turno_actual % len(self.jugadores)]
                
                if jugador_actual == jugador_desconectado:
                    logger.info("Jugador con turno activo se desconectó, reseteando estado...")
                    self._resetear_estado_turno()
    
    # ============================================
    # MÉTODOS DE DETERMINACIÓN DE TURNOS
    # ============================================
    
    def iniciar_determinacion_turnos(self):
        """
        Inicia la fase de determinación de turnos.
        Todos los jugadores deben lanzar los dados una vez.
        """
        with self.lock:
            if not self.puede_iniciar():
                logger.error("No hay suficientes jugadores para iniciar determinación")
                return False
            
            self.determinacion_activa = True
            self.tiradas_determinacion = {}
            self.jugadores_en_desempate = set()
            
            logger.info("✨ Iniciando fase de determinación de turnos")
            logger.info(f"Jugadores participantes: {[info['nombre'] for info in self.clientes.values()]}")
            return True
    
    def registrar_tirada_determinacion(self, websocket, dado1, dado2):
        """
        Registra la tirada de un jugador durante la determinación.
        Retorna: (fase_completa, resultado)
            - fase_completa: True si todos han tirado
            - resultado: dict con información del estado
        """
        with self.lock:
            if not self.determinacion_activa:
                return False, {"error": "No hay determinación activa"}
            
            if websocket not in self.clientes:
                return False, {"error": "Cliente no válido"}
            
            info = self.clientes[websocket]
            
            # Si hay desempate activo, verificar que este jugador deba tirar
            if self.jugadores_en_desempate:
                if websocket not in self.jugadores_en_desempate:
                    return False, {"error": "No estás en el desempate"}
            else:
                # Primera ronda: verificar que no haya tirado ya
                if websocket in self.tiradas_determinacion:
                    return False, {"error": "Ya realizaste tu tirada"}
            
            # Registrar tirada
            suma = dado1 + dado2
            self.tiradas_determinacion[websocket] = {
                'nombre': info['nombre'],
                'color': info['color'],
                'dado1': dado1,
                'dado2': dado2,
                'suma': suma
            }
            
            logger.info(f"📝 Tirada registrada: {info['nombre']} ({info['color']}) = [{dado1}][{dado2}] = {suma}")
            
            # Verificar si todos los jugadores requeridos han tirado
            if self.jugadores_en_desempate:
                # Modo desempate: solo esperamos a los jugadores en desempate
                jugadores_esperados = self.jugadores_en_desempate
            else:
                # Primera ronda: esperamos a todos
                jugadores_esperados = set(self.clientes.keys())
            
            jugadores_que_tiraron = set(self.tiradas_determinacion.keys())
            
            if not jugadores_esperados.issubset(jugadores_que_tiraron):
                # Aún faltan jugadores - determinar quién es el siguiente
                pendientes = len(jugadores_esperados - jugadores_que_tiraron)
                
                # Obtener el siguiente jugador que NO ha tirado (por ID)
                siguiente_ws = None
                siguiente_nombre = ""
                
                # Ordenar clientes por ID para determinar el orden
                clientes_ordenados = sorted(
                    [(ws, self.clientes[ws]) for ws in jugadores_esperados],
                    key=lambda x: x[1]['id']
                )
                
                # Encontrar el primer jugador que no ha tirado
                for ws, cliente_info in clientes_ordenados:
                    if ws not in jugadores_que_tiraron:
                        siguiente_ws = ws
                        siguiente_nombre = cliente_info['nombre']
                        break
                
                return False, {
                    "pendientes": pendientes,
                    "siguiente": siguiente_nombre
                }
            
            # Todos han tirado, analizar resultados
            return self._analizar_resultados_determinacion()
    
    def _analizar_resultados_determinacion(self):
        """
        Analiza los resultados de las tiradas y determina si hay ganador o empate.
        Retorna: (fase_completa, resultado)
        """
        with self.lock:
            if not self.tiradas_determinacion:
                return False, {"error": "No hay tiradas registradas"}
            
            # Encontrar el puntaje más alto
            max_suma = max(t['suma'] for t in self.tiradas_determinacion.values())
            
            # Encontrar todos los jugadores con el puntaje más alto
            jugadores_max = [
                (ws, datos) for ws, datos in self.tiradas_determinacion.items()
                if datos['suma'] == max_suma
            ]
            
            logger.info(f"🎯 Puntaje más alto: {max_suma}")
            logger.info(f"🎯 Jugadores con puntaje máximo: {[d['nombre'] for _, d in jugadores_max]}")
            
            if len(jugadores_max) == 1:
                # ¡Hay un ganador claro!
                websocket_ganador, datos_ganador = jugadores_max[0]
                return self._finalizar_determinacion(websocket_ganador, datos_ganador)
            else:
                # Empate: preparar nueva ronda solo con los empatados
                return self._preparar_desempate(jugadores_max, max_suma)
    
    def _preparar_desempate(self, jugadores_empatados, valor_empate):
        """
        Prepara una ronda de desempate entre los jugadores empatados.
        """
        with self.lock:
            # Limpiar tiradas anteriores
            self.tiradas_determinacion = {}
            
            # Marcar solo a los jugadores empatados para la siguiente ronda
            self.jugadores_en_desempate = {ws for ws, _ in jugadores_empatados}
            
            jugadores_info = [
                {
                    'nombre': datos['nombre'],
                    'color': datos['color'],
                    'suma': datos['suma']
                }
                for _, datos in jugadores_empatados
            ]
            
            logger.info(f"🔄 Empate detectado con {valor_empate} puntos")
            logger.info(f"🔄 Jugadores en desempate: {[j['nombre'] for j in jugadores_info]}")
            
            return False, {
                "empate": True,
                "jugadores": jugadores_info,
                "valor": valor_empate
            }
    
    def _finalizar_determinacion(self, websocket_ganador, datos_ganador):
        """
        Finaliza la determinación estableciendo el orden de turnos.
        """
        with self.lock:
            color_ganador = datos_ganador['color']
            
            # Secuencias fijas de turnos según el color ganador
            SECUENCIAS_TURNOS = {
                'rojo': ['rojo', 'verde', 'amarillo', 'azul'],
                'verde': ['verde', 'amarillo', 'azul', 'rojo'],
                'amarillo': ['amarillo', 'azul', 'rojo', 'verde'],
                'azul': ['azul', 'rojo', 'verde', 'amarillo']
            }
            
            secuencia = SECUENCIAS_TURNOS.get(color_ganador, ['rojo', 'verde', 'amarillo', 'azul'])
            
            logger.info(f"🏆 Ganador: {datos_ganador['nombre']} ({color_ganador})")
            logger.info(f"📋 Secuencia de turnos: {' -> '.join(secuencia)}")
            
            # Crear mapa de color -> websocket
            color_a_websocket = {
                info['color']: ws
                for ws, info in self.clientes.items()
            }
            
            # Ordenar jugadores según la secuencia
            self.orden_turnos_determinado = []
            for color in secuencia:
                if color in color_a_websocket:
                    ws = color_a_websocket[color]
                    self.orden_turnos_determinado.append(ws)
            
            # Reordenar la lista de jugadores según el orden determinado
            jugadores_ordenados = []
            for ws in self.orden_turnos_determinado:
                jugador = self.clientes[ws]['jugador']
                jugadores_ordenados.append(jugador)
            
            self.jugadores = jugadores_ordenados
            
            logger.info(f"✅ Orden final establecido: {' -> '.join([self.clientes[ws]['nombre'] for ws in self.orden_turnos_determinado])}")
            
            # Preparar información del orden para enviar al cliente
            orden_info = [
                {
                    'nombre': self.clientes[ws]['nombre'],
                    'color': self.clientes[ws]['color']
                }
                for ws in self.orden_turnos_determinado
            ]
            
            # Finalizar la determinación
            self.determinacion_activa = False
            self.tiradas_determinacion = {}
            self.jugadores_en_desempate = set()
            
            return True, {
                "ganador": {
                    'nombre': datos_ganador['nombre'],
                    'color': datos_ganador['color']
                },
                "orden": orden_info
            }
    
    # ============================================
    # FIN MÉTODOS DE DETERMINACIÓN DE TURNOS
    # ============================================
    
    def puede_iniciar(self):
        with self.lock:
            return len(self.jugadores) >= proto.MIN_JUGADORES
    
    def iniciar_juego(self):
        with self.lock:
            logger.debug("🔒 Iniciando juego")
            self.juego_iniciado = True
            self.turno_actual = 0
            self._resetear_estado_turno()
            logger.info("✅ Juego iniciado")
    
    def _resetear_estado_turno(self):
        """Resetea el estado del turno actual"""
        self.dados_lanzados = False
        self.dobles_consecutivos = 0
        self.accion_realizada = False
        self.debe_avanzar_turno = False
        self.dados_usados = []  # ⭐ NUEVO: Resetear dados usados
        self.premio_tres_dobles = False  # ⭐ NUEVO: Resetear premio
        logger.debug("🔄 Estado de turno reseteado")
    
    def obtener_jugador_actual(self):
        """MÉTODO SIN LOCK - usar solo cuando ya tienes el lock"""
        if not self.jugadores or self.juego_terminado:
            return None
        return self.jugadores[self.turno_actual % len(self.jugadores)]
    
    def obtener_jugador_actual_safe(self):
        """Versión segura con lock"""
        with self.lock:
            return self.obtener_jugador_actual()
    
    def es_turno_de(self, socket_cliente):
        """Verifica si es el turno del cliente"""
        with self.lock:
            logger.debug(f"🔒 Verificando turno para cliente")
            
            if socket_cliente not in self.clientes:
                logger.debug("Cliente no encontrado")
                return False
            
            jugador_actual = self.obtener_jugador_actual()
            if not jugador_actual:
                logger.debug("No hay jugador actual")
                return False
            
            es_turno = self.clientes[socket_cliente]["jugador"] == jugador_actual
            logger.debug(f"¿Es su turno? {es_turno}")
            return es_turno
    
    def puede_hacer_alguna_accion(self, socket_cliente):
        """⭐ NUEVO: Verifica si el jugador puede hacer alguna acción"""
        with self.lock:
            if socket_cliente not in self.clientes:
                return False
            
            jugador = self.clientes[socket_cliente]["jugador"]
            
            # Si salió doble, revisar fichas en cárcel
            if self.ultimo_es_doble:
                fichas_bloqueadas = [f for f in jugador.fichas if f.estado == proto.ESTADO_BLOQUEADO]
                if fichas_bloqueadas:
                    return True
                # ⭐ CONTINUAR verificando fichas en juego aunque no haya en cárcel
            
            # Revisar fichas EN_JUEGO (en tablero principal)
            fichas_en_tablero = [f for f in jugador.fichas 
                                if f.estado == proto.ESTADO_EN_JUEGO and
                                not (hasattr(f, 'posicion_meta') and f.posicion_meta is not None and f.posicion_meta >= 0)]
            
            # Si hay fichas en el tablero principal, puede moverlas
            if fichas_en_tablero:
                return True
            
            # Revisar fichas en CAMINO_META
            fichas_en_camino_meta = [f for f in jugador.fichas 
                                     if f.estado in [proto.ESTADO_EN_JUEGO, "CAMINO_META"] and
                                     hasattr(f, 'posicion_meta') and f.posicion_meta is not None and f.posicion_meta >= 0]
            
            # Verificar si alguna ficha en camino a meta puede moverse con los dados disponibles
            for ficha in fichas_en_camino_meta:
                pasos_restantes = 7 - ficha.posicion_meta
                # ⭐ CRÍTICO: Verificar dados individuales Y suma
                if self.ultimo_es_doble:
                    # Con dobles, puede usar cualquiera de los dos dados individuales O la suma
                    if self.ultimo_dado1 <= pasos_restantes or self.ultimo_dado2 <= pasos_restantes or self.ultima_suma <= pasos_restantes:
                        return True
                else:
                    # Sin dobles, puede usar dados individuales o suma
                    if self.ultimo_dado1 <= pasos_restantes or self.ultimo_dado2 <= pasos_restantes or self.ultima_suma <= pasos_restantes:
                        return True
            
            return False
    
    def lanzar_dados(self):
        """Lanza los dados - DEBE LLAMARSE CON LOCK EXTERNO"""
        logger.debug("🎲 Generando dados...")
        
        self.ultimo_dado1 = random.randint(1, 6)
        self.ultimo_dado2 = random.randint(1, 6)
        self.ultima_suma = self.ultimo_dado1 + self.ultimo_dado2
        self.ultimo_es_doble = self.ultimo_dado1 == self.ultimo_dado2
        self.dados_lanzados = True
        self.accion_realizada = False
        self.dados_usados = []  # ⭐ NUEVO: Reiniciar dados usados con cada tiro
        self.debe_avanzar_turno = False  # ⭐ CRÍTICO: Resetear flag con cada nuevo lanzamiento
        
        if self.ultimo_es_doble:
            self.dobles_consecutivos += 1
            
            # ⭐ PREMIO: Si llegó a 3 dobles, puede sacar una ficha del juego
            if self.dobles_consecutivos >= self.max_dobles:
                logger.info(f"🎉 ¡PREMIO! Jugador sacó {self.dobles_consecutivos} dobles consecutivos")
                logger.info("🏆 Puede elegir UNA ficha para enviarla a META (sacarla del juego)")
                self.premio_tres_dobles = True  # Nueva bandera
                self.debe_avanzar_turno = True  # Después de elegir, avanza turno
                # ⚠️ NO resetear ultimo_es_doble aquí - se hace al aplicar el premio
            else:
                self.debe_avanzar_turno = False
                logger.debug(f"¡DOBLES! ({self.dobles_consecutivos}/{self.max_dobles}) - Mantiene turno")
        else:
            self.dobles_consecutivos = 0
            # Ya no establecemos debe_avanzar_turno aquí, lo manejará el método mover_ficha
            logger.debug("Sin dobles - Verificar si puede hacer acciones")
        
        logger.info(f"🎲 Dados: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}")
        return self.ultimo_dado1, self.ultimo_dado2, self.ultima_suma, self.ultimo_es_doble
    
    def lanzar_dados_safe(self):
        """Versión segura de lanzar dados con lock"""
        with self.lock:
            return self.lanzar_dados()
    
    def necesita_pasar_turno_automaticamente(self, socket_cliente):
        """⭐ NUEVO: Determina si debe pasar el turno automáticamente"""
        with self.lock:
            if not self.dados_lanzados:
                return False
            
            # Si salió doble, NO pasar turno (puede sacar fichas)
            if self.ultimo_es_doble:
                return False
            
            # Si NO salió doble, verificar si puede hacer algo
            puede_actuar = self.puede_hacer_alguna_accion(socket_cliente)
            
            # Si no puede hacer nada, pasar turno automáticamente
            if not puede_actuar:
                logger.info("❗ Jugador no puede hacer ninguna acción - pasando turno automáticamente")
                return True
            
            return False
    
    def sacar_todas_fichas_carcel(self, socket_cliente):
        """Saca TODAS las fichas de la cárcel automáticamente cuando sale doble"""
        with self.lock:
            logger.debug("🔒 Intentando sacar todas las fichas de cárcel automáticamente")
            
            # ⭐ NUEVO: Si hay premio activo, rechazar
            if self.premio_tres_dobles:
                return False, "Debes elegir una ficha para el premio de 3 dobles primero"
            
            if socket_cliente not in self.clientes:
                return False, "Cliente no válido"
            
            jugador_actual = self.obtener_jugador_actual()
            if not jugador_actual or self.clientes[socket_cliente]["jugador"] != jugador_actual:
                return False, "No es tu turno"
            
            if not self.ultimo_es_doble:
                return False, "Necesitas dobles para liberar fichas"
            
            jugador = self.clientes[socket_cliente]["jugador"]
            color = self.clientes[socket_cliente]["color"]
            
            fichas_bloqueadas = [f for f in jugador.fichas if f.estado == proto.ESTADO_BLOQUEADO]
            if not fichas_bloqueadas:
                return False, "No tienes fichas en la cárcel"
            
            # Usar el nuevo sistema de salidas
            salida = self.tablero.salidas[color]  # Ahora es un diccionario
            fichas_liberadas = []
            capturas_todas = []  # Lista para acumular todas las capturas
            
            for ficha in fichas_bloqueadas:
                ficha.estado = proto.ESTADO_EN_JUEGO
                ficha.posicion = salida
                ficha_id = getattr(ficha, 'id', 0)
                fichas_liberadas.append(ficha_id)
                logger.info(f"🔓 Ficha {ficha_id} de {color} liberada automáticamente a posición {salida}")
                
                # ⭐ NUEVO: Ejecutar capturas para cada ficha liberada
                fichas_capturadas = self.ejecutar_capturas(salida, color, jugador)
                capturas_todas.extend(fichas_capturadas)
            
            # ⭐ Marcar acción realizada
            self.accion_realizada = True
            
            resultado = {"fichas_liberadas": fichas_liberadas, "posicion": salida}
            
            # Agregar información de capturas si hubo
            if capturas_todas:
                resultado["capturas"] = capturas_todas
            
            return True, resultado
    
    def sacar_de_carcel(self, socket_cliente):
        """Saca UNA ficha de la cárcel cuando sale doble"""
        with self.lock:
            logger.debug("🔒 Intentando sacar de cárcel")
            
            # ⭐ NUEVO: Si hay premio activo, rechazar
            if self.premio_tres_dobles:
                return False, "Debes elegir una ficha para el premio de 3 dobles primero"
            
            if socket_cliente not in self.clientes:
                return False, "Cliente no válido"
            
            jugador_actual = self.obtener_jugador_actual()
            if not jugador_actual or self.clientes[socket_cliente]["jugador"] != jugador_actual:
                return False, "No es tu turno"
            
            if not self.dados_lanzados:
                return False, "Debes lanzar los dados primero"
            
            if not self.ultimo_es_doble:
                return False, "Necesitas sacar dobles para liberar fichas"
            
            jugador = self.clientes[socket_cliente]["jugador"]
            color = self.clientes[socket_cliente]["color"]
            
            # Buscar fichas bloqueadas
            fichas_bloqueadas = [f for f in jugador.fichas if f.estado == proto.ESTADO_BLOQUEADO]
            
            if not fichas_bloqueadas:
                return False, "No tienes fichas en la cárcel"
            
            # Sacar la primera ficha bloqueada
            ficha = fichas_bloqueadas[0]
            # Usar el nuevo sistema de salidas
            salida = self.tablero.salidas[color]  # Ahora es un diccionario
            
            # Cambiar estado y posición
            ficha.estado = proto.ESTADO_EN_JUEGO
            ficha.posicion = salida
            
            ficha_id = getattr(ficha, 'id', 0)
            logger.info(f"🔓 Ficha {ficha_id} de {color} liberada a posición {salida}")
            
            # ⭐ NUEVO: Ejecutar capturas al salir de la cárcel
            fichas_capturadas = self.ejecutar_capturas(salida, color, jugador)
            
            # Marcar acción realizada
            self.accion_realizada = True
            
            resultado = {"ficha_id": ficha_id, "posicion": salida}
            
            # Agregar información de capturas si hubo
            if fichas_capturadas:
                resultado["capturas"] = fichas_capturadas
            
            return True, resultado
    
    def mover_ficha(self, socket_cliente, ficha_id, dado_elegido):
        """
        Mueve una ficha usando el dado elegido.
        dado_elegido: 1 = primer dado, 2 = segundo dado, 3 = suma de dados
        """
        with self.lock:
            logger.debug(f"Procesando movimiento de ficha {ficha_id} con dado {dado_elegido}")
            
            # ⭐ NUEVO: Si hay premio activo, rechazar movimiento normal
            if self.premio_tres_dobles:
                return False, "Debes elegir una ficha para el premio de 3 dobles primero (usa MSG_ELEGIR_FICHA_PREMIO)"
            
            # Validaciones básicas
            if not self.es_turno_de(socket_cliente):
                return False, "No es tu turno"

            if not self.dados_lanzados:
                return False, "Debes lanzar los dados primero"

            jugador = self.clientes[socket_cliente]["jugador"]
            
            if ficha_id < 0 or ficha_id >= len(jugador.fichas):
                return False, "Ficha inválida"

            ficha = jugador.fichas[ficha_id]
            
            # ⭐ NUEVO: Inicializar lista de dados usados si no existe
            if not hasattr(self, 'dados_usados'):
                self.dados_usados = []
            
            # Validar que el dado no haya sido usado ya
            if dado_elegido in [1, 2] and dado_elegido in self.dados_usados:
                return False, f"El dado {dado_elegido} ya fue usado"
            
            # Validar que la ficha no esté en cárcel o meta
            if ficha.estado == "BLOQUEADO":
                return False, "Esta ficha está en la cárcel"
            if ficha.estado == "META":
                return False, "Esta ficha ya está en meta"

            # Determinar el valor del movimiento según el dado elegido
            if dado_elegido == 1:
                valor_movimiento = self.ultimo_dado1
                logger.debug(f"Usando primer dado: {valor_movimiento}")
            elif dado_elegido == 2:
                valor_movimiento = self.ultimo_dado2
                logger.debug(f"Usando segundo dado: {valor_movimiento}")
            elif dado_elegido == 3:
                valor_movimiento = self.ultima_suma
                logger.debug(f"Usando suma de dados: {valor_movimiento}")
            else:
                logger.warning(f"Dado elegido inválido: {dado_elegido}")
                return False, "Opción de dado inválida"

            # ⭐ CRÍTICO: Contar fichas movibles REALES (que puedan usar AL MENOS un dado)
            fichas_movibles = 0
            
            for f in jugador.fichas:
                if f.estado == proto.ESTADO_BLOQUEADO or f.estado == proto.ESTADO_META:
                    continue
                
                # Fichas en tablero principal SIEMPRE pueden moverse
                if f.estado == proto.ESTADO_EN_JUEGO and not (hasattr(f, 'posicion_meta') and f.posicion_meta is not None and f.posicion_meta >= 0):
                    fichas_movibles += 1
                # Fichas en camino a meta: solo contar si pueden usar AL MENOS un dado
                elif hasattr(f, 'posicion_meta') and f.posicion_meta is not None and f.posicion_meta >= 0:
                    pasos_restantes_f = 7 - f.posicion_meta
                    # Verificar si puede usar algún dado individual (no suma)
                    if self.ultimo_dado1 <= pasos_restantes_f or self.ultimo_dado2 <= pasos_restantes_f:
                        fichas_movibles += 1
            
            # Validaciones según si está en camino a meta
            en_camino_meta = hasattr(ficha, 'posicion_meta') and ficha.posicion_meta is not None and ficha.posicion_meta >= 0
            
            if en_camino_meta:
                # ⭐ CORREGIDO: Permitir suma SI NO excede el límite
                pasos_restantes = 7 - ficha.posicion_meta
                if valor_movimiento > pasos_restantes:
                    return False, f"El movimiento excede la meta (necesitas máximo {pasos_restantes} pasos)"
                # ⭐ CRÍTICO: NO forzar suma en fichas en camino a meta
                # Las fichas en camino a meta pueden usar dados individuales libremente
                
            elif not en_camino_meta and fichas_movibles == 1 and not self.tablero.esta_cerca_meta(ficha) and len(self.dados_usados) == 0:
                # ⭐ CRÍTICO: Solo forzar suma si:
                # - NO está en camino a meta
                # - Tiene solo 1 ficha movible
                # - La ficha NO está cerca de meta
                # - NO se ha usado ningún dado aún
                if dado_elegido != 3:
                    return False, "Debes usar la suma de dados cuando tienes una sola ficha lejos de meta"

            # Intentar realizar el movimiento
            posicion_anterior = ficha.posicion
            logger.debug(f"Intentando mover ficha desde {posicion_anterior} con valor {valor_movimiento}")
            
            if ficha.mover(valor_movimiento, self.tablero):
                self.accion_realizada = True
                logger.info(f"Ficha {ficha_id} movida de {posicion_anterior} a {ficha.posicion}")
                
                # ⭐ NUEVO: Marcar dados como usados DESPUÉS del movimiento exitoso
                if dado_elegido == 3:
                    # Usó la suma → marcar ambos dados como usados
                    self.debe_avanzar_turno = True
                    self.dados_usados = [1, 2]
                    logger.debug("Suma usada → ambos dados marcados como usados")
                elif dado_elegido in [1, 2]:
                    # Registrar dado individual usado
                    self.dados_usados.append(dado_elegido)
                    logger.debug(f"Dado {dado_elegido} registrado como usado. Dados usados: {self.dados_usados}")
                    
                    # ⭐ CRÍTICO: Verificar si el dado restante es utilizable (CON O SIN DOBLES)
                    if len(self.dados_usados) == 1:
                        # Determinar cuál dado queda
                        dado_restante_valor = self.ultimo_dado2 if dado_elegido == 1 else self.ultimo_dado1
                        
                        # Verificar si ALGUNA ficha puede usar el dado restante
                        puede_usar_restante = False
                        
                        for f in jugador.fichas:
                            if f.estado == proto.ESTADO_BLOQUEADO or f.estado == proto.ESTADO_META:
                                continue
                            
                            # Verificar si está en camino a meta
                            en_camino = hasattr(f, 'posicion_meta') and f.posicion_meta is not None and f.posicion_meta >= 0
                            
                            if en_camino:
                                pasos_rest = 7 - f.posicion_meta
                                if dado_restante_valor <= pasos_rest:
                                    puede_usar_restante = True
                                    break
                            else:  # En tablero principal
                                puede_usar_restante = True
                                break
                        
                        if not puede_usar_restante:
                            logger.info(f"⚠️ El dado restante ({dado_restante_valor}) no puede ser usado. Forzando avance de turno.")
                            # ⭐ Con dobles: mantiene turno pero resetea dados
                            if self.ultimo_es_doble:
                                self.dados_usados = []  # Resetear para permitir nuevo lanzamiento
                                logger.info("🔄 Dobles: mantiene turno, reseteando dados usados")
                            else:
                                # Sin dobles: avanza turno
                                self.debe_avanzar_turno = True
                
                # ⭐ NUEVO: Ejecutar capturas si la ficha está EN_JUEGO
                fichas_capturadas = []
                if ficha.estado == proto.ESTADO_EN_JUEGO:
                    fichas_capturadas = self.ejecutar_capturas(
                        ficha.posicion, 
                        jugador.color,
                        jugador
                    )
                
                # Verificar victoria si llegó a meta
                if ficha.estado == "META":
                    self.verificar_victoria(socket_cliente)
                
                resultado = {
                    "desde": posicion_anterior,
                    "hasta": ficha.posicion
                }
                
                # Agregar información de capturas si hubo
                if fichas_capturadas:
                    resultado["capturas"] = fichas_capturadas
                
                return True, resultado
            
            return False, "Movimiento inválido"
    
    def debe_avanzar_turno_ahora(self):
        """Determina si debe avanzar el turno después de una acción"""
        with self.lock:
            # Si no ha hecho una acción, no avanzar
            if not self.accion_realizada:
                return False
            
            # Si salió doble y no excede el límite, NO avanzar (mantener turno)
            if self.ultimo_es_doble and self.dobles_consecutivos < self.max_dobles:
                logger.debug("🔄 Dobles: mantiene turno")
                return False
            
            # Si se usó la suma de dados, avanzar turno
            if self.debe_avanzar_turno:
                logger.debug("➡️ Debe avanzar turno: se usó la suma")
                return True
                
            # Si se usaron ambos dados individuales, avanzar turno
            if hasattr(self, 'dados_usados') and len(self.dados_usados) == 2:
                logger.debug("➡️ Debe avanzar turno: se usaron ambos dados")
                return True
                
            return False
    
    def avanzar_turno(self):
        """Avanzar al siguiente turno con lógica corregida"""
        with self.lock:
            logger.debug("🔒 Avanzando turno")
            
            if len(self.jugadores) == 0:
                return False
            
            # Si salió doble y no excede el límite, mantener turno
            if self.ultimo_es_doble and self.dobles_consecutivos < self.max_dobles:
                logger.info(f"🔄 Doble! El jugador mantiene su turno (dobles: {self.dobles_consecutivos})")
                # ⭐ CRÍTICO: Solo resetear si usó AMBOS dados
                if len(self.dados_usados) == 2:
                    # Usó ambos dados → permitir lanzar de nuevo
                    self.dados_lanzados = False
                    self.dados_usados = []
                    logger.debug("🔄 Usó ambos dados → puede lanzar de nuevo")
                else:
                    # Aún tiene dados sin usar → NO resetear dados_lanzados
                    logger.debug(f"🔄 Aún tiene {2 - len(self.dados_usados)} dado(s) sin usar → mantiene dados_lanzados=True")
                
                # Siempre resetear estas banderas
                self.accion_realizada = False
                self.debe_avanzar_turno = False
                return False  # NO avanzó turno
            
            # Avanzar al siguiente jugador
            turno_anterior = self.turno_actual
            self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
            
            # Resetear TODO el estado del turno
            self._resetear_estado_turno()
            
            logger.info(f"➡️ Turno avanzado del jugador {turno_anterior} al {self.turno_actual}")
            return True  # SÍ avanzó turno
    
    def forzar_avance_turno(self):
        """⭐ NUEVO: Fuerza el avance de turno cuando no puede hacer acciones"""
        with self.lock:
            if len(self.jugadores) > 0:
                turno_anterior = self.turno_actual
                self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
                self._resetear_estado_turno()
                logger.info(f"🔄 Turno forzado: {turno_anterior} → {self.turno_actual}")
                return True
            return False
    
    def verificar_victoria(self, socket_cliente):
        with self.lock:
            if socket_cliente not in self.clientes:
                return False
            
            jugador = self.clientes[socket_cliente]["jugador"]
            info = self.clientes[socket_cliente]
            
            try:
                ha_ganado = jugador.ha_ganado()
                
                if ha_ganado:
                    # Marcar jugador como terminado (agregar flag)
                    info["terminado"] = True
                    jugador.terminado = True  # También en el objeto User
                    
                    logger.info(f"🏆 ¡Jugador {info['nombre']} ({info['color']}) completó todas sus fichas!")
                    
                    # Contar jugadores activos (no terminados)
                    jugadores_activos = sum(
                        1 for cli_info in self.clientes.values()
                        if not cli_info.get("terminado", False)
                    )
                    
                    logger.info(f"📊 Jugadores activos restantes: {jugadores_activos}")
                    
                    # Si solo queda 1 jugador activo (o ninguno), terminar el juego
                    if jugadores_activos <= 1:
                        self.juego_terminado = True
                        logger.info(f"🎊 ¡JUEGO TERMINADO! Solo queda {jugadores_activos} jugador(es) activo(s)")
                
                return ha_ganado
            except Exception as e:
                logger.error(f"Error verificando victoria: {e}", exc_info=True)
                return False
    
    def obtener_estado_tablero(self):
        """Obtiene el estado completo del tablero"""
        with self.lock:
            logger.debug("🔒 Obteniendo estado del tablero")
            
            estado = {
                "jugadores": [],
                "turno_actual": self.turno_actual,
                "dados_lanzados": self.dados_lanzados,
                "ultimo_dado1": self.ultimo_dado1,
                "ultimo_dado2": self.ultimo_dado2,
                "ultima_suma": self.ultima_suma,
                "ultimo_es_doble": self.ultimo_es_doble,
                "dobles_consecutivos": self.dobles_consecutivos,
                "accion_realizada": self.accion_realizada,
                "debe_avanzar_turno": self.debe_avanzar_turno
            }
            
            for cliente_sock, info in self.clientes.items():
                jugador = info["jugador"]
                fichas_info = []
                
                for idx, ficha in enumerate(jugador.fichas):
                    ficha_data = {
                        "id": idx,
                        "color": ficha.color,
                        "estado": ficha.estado,
                        "posicion": ficha.posicion
                    }
                    
                    # ⭐ CRÍTICO: SIEMPRE incluir posicion_meta si estado es CAMINO_META
                    if ficha.estado == "CAMINO_META":
                        # Si está en CAMINO_META, DEBE tener posicion_meta
                        if hasattr(ficha, 'posicion_meta') and ficha.posicion_meta is not None:
                            ficha_data["posicion_meta"] = ficha.posicion_meta
                        else:
                            # Fallback: Si no tiene posicion_meta, usar 0
                            ficha_data["posicion_meta"] = 0
                            logger.warning(f"⚠️ Ficha en CAMINO_META sin posicion_meta, usando 0")
                    elif hasattr(ficha, 'posicion_meta') and ficha.posicion_meta is not None and ficha.posicion_meta >= 0:
                        # Para otros estados, solo si existe y es válido
                        ficha_data["posicion_meta"] = ficha.posicion_meta
                    
                    fichas_info.append(ficha_data)
                
                estado["jugadores"].append({
                    "nombre": info["nombre"],
                    "color": info["color"],
                    "id": info["id"],
                    "fichas": fichas_info,
                    "bloqueadas": len([f for f in jugador.fichas if f.estado == proto.ESTADO_BLOQUEADO]),
                    "en_juego": len([f for f in jugador.fichas if f.estado == proto.ESTADO_EN_JUEGO]),
                    "en_meta": len([f for f in jugador.fichas if f.estado == proto.ESTADO_META])
                })
            
            return estado
    
    def obtener_info_jugadores(self):
        """Obtiene información básica de todos los jugadores"""
        with self.lock:
            return [
                {
                    "nombre": info["nombre"],
                    "color": info["color"],
                    "id": info["id"]
                }
                for info in self.clientes.values()
            ]
    
    def esta_cerca_de_meta(self, ficha):
        """Verifica si una ficha está cerca de su meta"""
        return self.tablero.esta_cerca_meta(ficha)
    
    def obtener_fichas_en_casilla(self, casilla, excluir_color=None):
        """
        Obtiene todas las fichas presentes en una casilla específica.
        
        Args:
            casilla: índice de la casilla (0-indexed)
            excluir_color: color a excluir de la búsqueda (opcional)
            
        Returns:
            Lista de diccionarios con información de las fichas encontradas:
            [{'jugador': User, 'ficha': gameToken, 'ficha_id': int}, ...]
        """
        fichas_encontradas = []
        
        for jugador in self.jugadores:
            # Si se especifica un color a excluir y este jugador es de ese color, saltar
            if excluir_color and jugador.color == excluir_color:
                continue
            
            # Buscar fichas de este jugador en la casilla
            for idx, ficha in enumerate(jugador.fichas):
                # Solo considerar fichas en juego
                if ficha.estado == proto.ESTADO_EN_JUEGO and ficha.posicion == casilla:
                    fichas_encontradas.append({
                        'jugador': jugador,
                        'ficha': ficha,
                        'ficha_id': idx
                    })
        
        return fichas_encontradas
    
    def ejecutar_capturas(self, casilla_destino, color_atacante, jugador_atacante):
        """
        Ejecuta las capturas en una casilla específica.
        
        Args:
            casilla_destino: índice de la casilla donde se produjo el movimiento
            color_atacante: color de la ficha que llegó
            jugador_atacante: objeto User del jugador atacante
            
        Returns:
            Lista de fichas capturadas: [{'nombre': str, 'color': str, 'ficha_id': int}, ...]
        """
        fichas_capturadas = []
        
        with self.lock:
            # Verificar si se puede capturar en esta casilla
            if not self.tablero.puede_capturar_en_casilla(casilla_destino, color_atacante):
                logger.debug(f"No se puede capturar en casilla {casilla_destino} con color {color_atacante}")
                return fichas_capturadas
            
            # Obtener fichas enemigas en la casilla
            fichas_en_casilla = self.obtener_fichas_en_casilla(casilla_destino, excluir_color=color_atacante)
            
            if not fichas_en_casilla:
                logger.debug(f"No hay fichas enemigas en casilla {casilla_destino}")
                return fichas_capturadas
            
            # Capturar cada ficha enemiga
            for ficha_info in fichas_en_casilla:
                jugador_victima = ficha_info['jugador']
                ficha_victima = ficha_info['ficha']
                ficha_id = ficha_info['ficha_id']
                
                # Enviar ficha a la cárcel
                ficha_victima.estado = proto.ESTADO_BLOQUEADO
                ficha_victima.posicion = -1
                
                # Registrar captura
                fichas_capturadas.append({
                    'nombre': jugador_victima.name,
                    'color': jugador_victima.color,
                    'ficha_id': ficha_id
                })
                
                logger.info(f"🍽️ CAPTURA: {color_atacante} capturó ficha de {jugador_victima.color} "
                           f"(ID: {ficha_id}) en casilla {casilla_destino}")
            
            return fichas_capturadas
        
    def aplicar_premio_tres_dobles(self, socket_cliente, ficha_id):
        """
        Aplica el premio por sacar 3 dobles consecutivos:
        - Envía la ficha elegida directamente a META
        - Resetea dobles consecutivos
        - Avanza el turno
        
        Args:
            socket_cliente: websocket del jugador
            ficha_id: ID de la ficha a enviar a META
        
        Returns:
            tuple: (exito, resultado)
        """
        with self.lock:
            if socket_cliente not in self.clientes:
                return False, {"error": "Cliente no válido"}
            
            if not self.premio_tres_dobles:
                return False, {"error": "No tienes premio de 3 dobles activo"}
            
            jugador = self.clientes[socket_cliente]["jugador"]
            nombre = self.clientes[socket_cliente]["nombre"]
            color = self.clientes[socket_cliente]["color"]
            
            # ⭐ NUEVO: Obtener fichas elegibles primero
            fichas_elegibles = []
            for idx, f in enumerate(jugador.fichas):
                if f.estado == proto.ESTADO_EN_JUEGO:
                    fichas_elegibles.append(idx)
            
            # Si no hay fichas elegibles
            if not fichas_elegibles:
                return False, {"error": "No tienes fichas elegibles (todas en cárcel o meta)"}
            
            # ⭐ CRÍTICO: Validar que ficha_id esté en la lista de elegibles
            logger.info(f"🔍 Validando ficha_id={ficha_id}, elegibles={fichas_elegibles}")
            
            if ficha_id not in fichas_elegibles:
                # Mantener premio activo para que pueda reintentar
                logger.warning(f"❌ Ficha {ficha_id} no está en la lista de elegibles: {fichas_elegibles}")
                nombres_fichas = ', '.join([f"#{f + 1}" for f in fichas_elegibles])
                return False, {"error": f"Ficha #{ficha_id + 1} no es elegible. Fichas disponibles: {nombres_fichas}"}
            
            # Validar rango (redundante pero por seguridad)
            if ficha_id < 0 or ficha_id >= len(jugador.fichas):
                return False, {"error": "Ficha inválida"}
            
            ficha = jugador.fichas[ficha_id]
            
            # Validar que la ficha esté en juego
            if ficha.estado != proto.ESTADO_EN_JUEGO:
                return False, {"error": "Solo puedes enviar a META fichas que estén en el tablero"}
            
            # Guardar información anterior
            estado_anterior = ficha.estado
            posicion_anterior = ficha.posicion
            en_camino_meta = hasattr(ficha, 'posicion_meta') and ficha.posicion_meta is not None and ficha.posicion_meta >= 0
            
            # Enviar ficha directamente a META
            ficha.estado = proto.ESTADO_META
            ficha.posicion = -1  # Meta final
            if en_camino_meta:
                ficha.posicion_meta = 8  # Posición final en meta
            
            logger.info(f"🏆 PREMIO: Ficha {ficha_id} de {nombre} ({color}) "
                       f"enviada a META desde {'camino a meta' if en_camino_meta else f'casilla {posicion_anterior}'}")
            
            # Resetear estado completamente (importante: también ultimo_es_doble)
            self.premio_tres_dobles = False
            self.dobles_consecutivos = 0
            self.ultimo_es_doble = False  # ⭐ CRÍTICO: Evitar que mantenga el turno
            self.accion_realizada = True
            self.debe_avanzar_turno = True  # ⭐ FORZAR avance de turno
            
            # Verificar si ganó con esta ficha
            if jugador.ha_ganado():
                self.juego_terminado = True
                logger.info(f"🎊 ¡{nombre} ha ganado el juego con el premio de 3 dobles!")
            
            return True, {
                "ficha_id": ficha_id,
                "color": color,
                "desde": posicion_anterior,
                "estado_anterior": estado_anterior,
                "ha_ganado": self.juego_terminado
            }
    
    def obtener_fichas_elegibles_para_premio(self, socket_cliente):
        """
        Obtiene la lista de fichas que pueden ser enviadas a META con el premio.
        Solo fichas en EN_JUEGO o CAMINO_META.
        
        Returns:
            list: Lista de IDs de fichas elegibles
        """
        with self.lock:
            try:
                if socket_cliente not in self.clientes:
                    logger.warning("Socket no encontrado en clientes")
                    return []
                
                jugador = self.clientes[socket_cliente]["jugador"]
                fichas_elegibles = []
                
                logger.debug(f"Buscando fichas elegibles para {jugador.name}...")
                
                for idx, ficha in enumerate(jugador.fichas):
                    logger.debug(f"Ficha {idx}: estado={ficha.estado}, pos={ficha.posicion}")
                    
                    # ⭐ CORRECCIÓN: Solo fichas EN_JUEGO son elegibles (CAMINO_META no existe en protocol.py)
                    if ficha.estado == proto.ESTADO_EN_JUEGO:
                        ficha_info = {
                            "id": idx,
                            "estado": ficha.estado,
                            "color": ficha.color,
                            "posicion": ficha.posicion
                        }
                        
                        # Verificar si tiene posicion_meta (fichas en camino a meta)
                        if hasattr(ficha, 'posicion_meta') and ficha.posicion_meta is not None and ficha.posicion_meta >= 0:
                            ficha_info["posicion_meta"] = ficha.posicion_meta
                            ficha_info["en_camino_meta"] = True
                        else:
                            ficha_info["posicion_meta"] = None
                            ficha_info["en_camino_meta"] = False
                        
                        fichas_elegibles.append(ficha_info)
                        logger.debug(f"✅ Ficha {idx} es elegible: {ficha_info}")
                
                logger.info(f"📊 Total fichas elegibles: {len(fichas_elegibles)}")
                return fichas_elegibles
                
            except Exception as e:
                logger.error(f"Error en obtener_fichas_elegibles_para_premio: {e}", exc_info=True)
                return []
        
    def forzar_tres_dobles_debug(self, socket_cliente):
        """
        🔧 MÉTODO DE DEBUG: Simula que el jugador sacó 3 dobles consecutivos
        """
        with self.lock:
            if socket_cliente not in self.clientes:
                return False, "Cliente no válido"
            
            if not self.es_turno_de(socket_cliente):
                return False, "No es tu turno"
            
            # Simular dados dobles
            self.ultimo_dado1 = 6
            self.ultimo_dado2 = 6
            self.ultima_suma = 12
            self.ultimo_es_doble = True
            self.dados_lanzados = True
            self.accion_realizada = False
            self.dados_usados = []
            
            # Activar premio de 3 dobles
            self.dobles_consecutivos = 3
            self.premio_tres_dobles = True
            self.debe_avanzar_turno = True
            
            logger.warning("🔧 DEBUG: Forzados 3 dobles consecutivos - Premio activado")
            
            return True, {
                "dado1": self.ultimo_dado1,
                "dado2": self.ultimo_dado2,
                "suma": self.ultima_suma,
                "dobles_consecutivos": self.dobles_consecutivos
            }
