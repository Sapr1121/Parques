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
        
        # Control de estado de turno
        self.accion_realizada = False
        self.debe_avanzar_turno = False
    
    def agregar_jugador(self, websocket, nombre, color_elegido=None):
        """
        Agrega un jugador al juego.
        Args:
            websocket: conexión del cliente
            nombre: nombre del jugador
            color_elegido: color seleccionado por el jugador (opcional)
        
        Retorna: (color, error, es_admin, es_host)
        """
        with self.lock:
            logger.debug(f"🔒 Agregando jugador {nombre} con color preferido: {color_elegido}")

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
                "id": jugador_id
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
            
            # Revisar fichas en juego y en camino a meta
            fichas_movibles = [f for f in jugador.fichas 
                              if f.estado in ["EN_JUEGO", "CAMINO_META"]]
            
            if not fichas_movibles:
                return False
                
            # Verificar si alguna ficha puede moverse
            for ficha in fichas_movibles:
                if ficha.estado == "CAMINO_META":
                    # Verificar si puede moverse con algún dado individual
                    pasos_restantes = 7 - ficha.posicion_meta
                    if min(self.ultimo_dado1, self.ultimo_dado2) <= pasos_restantes:
                        return True
                else:  # EN_JUEGO
                    return True  # Siempre puede moverse en el tablero principal
            
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
        
        if self.ultimo_es_doble:
            self.dobles_consecutivos += 1
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
            
            for ficha in fichas_bloqueadas:
                ficha.estado = proto.ESTADO_EN_JUEGO
                ficha.posicion = salida
                ficha_id = getattr(ficha, 'id', 0)
                fichas_liberadas.append(ficha_id)
                logger.info(f"🔓 Ficha {ficha_id} de {color} liberada automáticamente a posición {salida}")
            
            # ⭐ Marcar acción realizada
            self.accion_realizada = True
            
            return True, {"fichas_liberadas": fichas_liberadas, "posicion": salida}
    
    def sacar_de_carcel(self, socket_cliente):
        """Saca UNA ficha de la cárcel cuando sale doble"""
        with self.lock:
            logger.debug("🔒 Intentando sacar de cárcel")
            
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
            
            # Marcar acción realizada
            self.accion_realizada = True
            
            return True, {"ficha_id": ficha_id, "posicion": salida}
    
    def mover_ficha(self, socket_cliente, ficha_id, dado_elegido):
        """
        Mueve una ficha usando el dado elegido.
        dado_elegido: 1 = primer dado, 2 = segundo dado, 3 = suma de dados
        """
        with self.lock:
            logger.debug(f"Procesando movimiento de ficha {ficha_id} con dado {dado_elegido}")
            
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
                
            # ⭐ NUEVO: Establecer flag para avanzar turno si:
            # 1. Se usa la suma de dados (dado_elegido = 3)
            # 2. Ya se usó un dado y estamos usando el otro (solo si no es dobles)
            if dado_elegido == 3:
                self.debe_avanzar_turno = True
            elif dado_elegido in [1, 2] and not self.ultimo_es_doble:  # Solo si no es dobles
                if len(self.dados_usados) == 1 and dado_elegido not in self.dados_usados:
                    self.debe_avanzar_turno = True
            
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

            # Contar fichas en juego y validar reglas especiales
            fichas_en_juego = sum(1 for f in jugador.fichas if f.estado in ["EN_JUEGO", "CAMINO_META"])
            
            # Validaciones según el estado de la ficha
            if ficha.estado == "CAMINO_META":
                if dado_elegido == 3:
                    return False, "No puedes usar la suma de dados en el camino a meta"
                    
                # Validar que no exceda el límite de la meta
                pasos_restantes = 7 - ficha.posicion_meta
                if valor_movimiento > pasos_restantes:
                    return False, "El movimiento excede la meta"
                
            elif fichas_en_juego == 1 and not self.tablero.esta_cerca_meta(ficha):
                # Con una sola ficha lejos de meta, debe usar la suma
                if dado_elegido != 3:
                    return False, "Debes usar la suma de dados cuando tienes una sola ficha lejos de meta"

            # Intentar realizar el movimiento
            posicion_anterior = ficha.posicion
            logger.debug(f"Intentando mover ficha desde {posicion_anterior} con valor {valor_movimiento}")
            
            if ficha.mover(valor_movimiento, self.tablero):
                self.accion_realizada = True
                logger.info(f"Ficha {ficha_id} movida de {posicion_anterior} a {ficha.posicion}")
                
                # ⭐ NUEVO: Registrar dado usado si es individual
                if dado_elegido in [1, 2]:
                    self.dados_usados.append(dado_elegido)
                    logger.debug(f"Dado {dado_elegido} registrado como usado. Dados usados: {self.dados_usados}")
                
                # Verificar victoria si llegó a meta
                if ficha.estado == "META":
                    self.verificar_victoria(socket_cliente)
                
                return True, {
                    "desde": posicion_anterior,
                    "hasta": ficha.posicion
                }
            
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
                # Resetear banderas de control pero mantener dobles_consecutivos
                self.dados_lanzados = False
                self.accion_realizada = False
                self.debe_avanzar_turno = False
                self.dados_usados = []  # ⭐ IMPORTANTE: Reiniciar dados usados
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
            try:
                ha_ganado = jugador.ha_ganado()
                
                if ha_ganado:
                    self.juego_terminado = True
                    logger.info(f"🏆 ¡Jugador {jugador.nombre} ha ganado!")
                
                return ha_ganado
            except Exception as e:
                logger.error(f"Error verificando victoria: {e}")
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
                    fichas_info.append({
                        "id": idx,
                        "color": ficha.color,
                        "estado": ficha.estado,
                        "posicion": ficha.posicion
                    })
                
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
