import asyncio
import websockets
import json
import time
import protocol as proto
import logging
# Desactivar logs de websockets
logging.getLogger('websockets').setLevel(logging.ERROR)  # o logging.WARNING

class ParchisClient:
    def __init__(self, servidor_ip, servidor_puerto):
        self.servidor_ip = servidor_ip
        self.servidor_puerto = servidor_puerto
        self.websocket = None
        self.conectado = False
        self.running = False

        self._last_missing = None
        self._last_conectados = None
        self._last_requeridos = None

        # Estado de administrador
        self.es_admin = False
        
        # Información del jugador
        self.mi_nombre = ""
        self.mi_color = ""
        self.mi_id = -1
        
        # Estado del juego
        self.conectados = 0
        self.requeridos = proto.MIN_JUGADORES

        self.juego_iniciado = False
        self.es_mi_turno = False
        self.jugadores = []
        self.estado_tablero = {}
        
        # Estado de dados y turnos
        self.dados_lanzados = False
        self.ultimo_dado1 = 0
        self.ultimo_dado2 = 0
        self.ultima_suma = 0
        self.ultimo_es_doble = False
        self.dobles_consecutivos = 0
        self.dados_usados = []
        
        # Control de flujo mejorado
        self.esperando_dados = False
        self.esperando_movimiento = False
        self.ultimo_movimiento_exitoso = False
        
        # ⭐ NUEVO: Estado de determinación de turnos
        self.en_determinacion = False
        self.mi_turno_determinado = False
        self.ya_lance_en_determinacion = False
        self.jugadores_en_desempate = []
        self.estoy_en_desempate = False
        
        # Cola de mensajes (asyncio.Queue)
        self.cola_mensajes = None
        
        # Debug
        self.debug = False



        # Aqui nosotros vamos a manejar el algoritmo de sincronizacion
        self.clock_offset = 0.0
        self.rtt_promedio = 0.0
        self.sincronizado = False
        self.historial_offsets = []

    """
    sincronizar_reloj()
_esperar_sync_response()
_calcular_std()
obtener_tiempo_sincronizado()
mostrar_info_sincronizacion()
    """

    async def sincronizar_reloj(self, rondas=5):

        print("\n" + "="*60)
        print("⏱️  SINCRONIZACIÓN DE RELOJ".center(60))
        print("="*60)
        print(f"Realizando {rondas} rondas de sincronización...")
    
        offsets = []
        rtts = []
    
        for ronda in range(rondas):
            try:
                # T1: Timestamp del cliente al enviar
                t1 = time.time()
            
                # Enviar solicitud de sincronización
                await self.enviar(proto.mensaje_sync_request(t1))
            
                # Esperar respuesta (con timeout)
                respuesta = await self._esperar_sync_response(timeout=2.0)
            
                if not respuesta:
                    print(f"⚠️  Ronda {ronda + 1}/{rondas}: Timeout")
                    continue
            
                # T4: Timestamp del cliente al recibir
                t4 = time.time()
            
                # Extraer timestamps del servidor
                t1_eco = respuesta.get("t1")
                t2 = respuesta.get("t2")  # Servidor recibió
                t3 = respuesta.get("t3")  # Servidor envió
            
                # Verificar que T1 coincida (validación)
                if abs(t1 - t1_eco) > 0.001:  # Tolerancia de 1ms
                    print(f"⚠️  Ronda {ronda + 1}/{rondas}: T1 no coincide")
                    continue
            
                # Calcular RTT (Round Trip Time)
                rtt = (t4 - t1) - (t3 - t2)
            
                # Calcular offset del reloj
                # offset = ((T2 - T1) + (T3 - T4)) / 2
                offset = ((t2 - t1) + (t3 - t4)) / 2
            
                offsets.append(offset)
                rtts.append(rtt)
            
                print(f"✓ Ronda {ronda + 1}/{rondas}: "
                    f"offset={offset*1000:.2f}ms, RTT={rtt*1000:.2f}ms")
            
            except Exception as e:
                print(f"❌ Error en ronda {ronda + 1}: {e}")
                continue
    
        if not offsets:
            print("\n❌ Sincronización FALLIDA: No se completó ninguna ronda")
            return False
    
        # Calcular promedios
        self.clock_offset = sum(offsets) / len(offsets)
        self.rtt_promedio = sum(rtts) / len(rtts)
        self.historial_offsets = offsets
        self.sincronizado = True
    
        # Mostrar resultados
        print("\n" + "-"*60)
        print("📊 RESULTADOS DE SINCRONIZACIÓN:")
        print(f"   • Offset del reloj: {self.clock_offset*1000:.2f} ms")
        print(f"   • RTT promedio: {self.rtt_promedio*1000:.2f} ms")
        print(f"   • Desviación estándar: {self._calcular_std(offsets)*1000:.2f} ms")
        print(f"   • Rondas exitosas: {len(offsets)}/{rondas}")
        print("="*60 + "\n")
    
        return True
    
    async def _esperar_sync_response(self, timeout=2.0):

        tiempo_inicio = time.time()
    
        while (time.time() - tiempo_inicio) < timeout:
            # Procesar mensajes de la cola
            if not self.cola_mensajes.empty():
                try:
                    mensaje = self.cola_mensajes.get_nowait()
                
                    # Si es SYNC_RESPONSE, devolverlo
                    if mensaje.get("tipo") == proto.MSG_SYNC_RESPONSE:
                        return mensaje
                    else:
                        # Si es otro mensaje, volver a ponerlo en la cola
                        await self.cola_mensajes.put(mensaje)
                    
                except asyncio.QueueEmpty:
                    pass
        
            await asyncio.sleep(0.01)  # 10ms
    
        return None

    def _calcular_std(self, valores):
        """Calcula la desviación estándar de una lista de valores"""
        if len(valores) < 2:
            return 0.0
    
        promedio = sum(valores) / len(valores)
        varianza = sum((x - promedio) ** 2 for x in valores) / len(valores)
        return varianza ** 0.5

    def obtener_tiempo_sincronizado(self):

        if not self.sincronizado:
            print("⚠️  Advertencia: Reloj no sincronizado, usando tiempo local")
            return time.time()
    
        return time.time() + self.clock_offset

    def mostrar_info_sincronizacion(self):
        """Muestra información sobre la sincronización actual"""
        if not self.sincronizado:
            print("⚠️  Reloj NO sincronizado")
            return
    
        print("\n" + "="*60)
        print("⏱️  INFORMACIÓN DE SINCRONIZACIÓN".center(60))
        print("="*60)
        print(f"Estado: {'✅ SINCRONIZADO' if self.sincronizado else '❌ NO SINCRONIZADO'}")
        print(f"Offset del reloj: {self.clock_offset*1000:.2f} ms")
        print(f"RTT promedio: {self.rtt_promedio*1000:.2f} ms")
    
        if self.historial_offsets:
            print(f"Mejor offset: {min(self.historial_offsets)*1000:.2f} ms")
            print(f"Peor offset: {max(self.historial_offsets)*1000:.2f} ms")
            print(f"Desviación estándar: {self._calcular_std(self.historial_offsets)*1000:.2f} ms")
    
        print(f"\nTiempo local: {time.time():.6f}")
        print(f"Tiempo sincronizado: {self.obtener_tiempo_sincronizado():.6f}")
        print("="*60)
    
        
    def log_debug(self, mensaje):
        """Logging para debug"""
        if self.debug:
            print(f"[DEBUG] {mensaje}")
    
    async def conectar(self, nombre):
        """Conecta al servidor WebSocket"""
        try:
            uri = f"ws://{self.servidor_ip}:{self.servidor_puerto}"
            print(f"\n🔍 DEBUG: Intentando conectar a {uri}")
            
            self.websocket = await websockets.connect(
                uri,
                ping_interval=20,
                ping_timeout=10
            )
            
            print(f"🔍 DEBUG: WebSocket object creado: {self.websocket}")
            
            # ✅ CORRECCIÓN: Verificar estado correctamente en websockets 15.x
            try:
                print(f"🔍 DEBUG: WebSocket conectado correctamente")
            except Exception as e:
                print(f"❌ Error verificando conexión: {e}")
                return False
            
            self.conectado = True
            self.running = True
            self.mi_nombre = nombre
            self.cola_mensajes = asyncio.Queue()
            
            print(f"✅ Conectado al servidor {uri}")

            print(f"🔍 DEBUG: Iniciando tarea de recepción")
            asyncio.create_task(self.recibir_mensajes())

            await asyncio.sleep(0.1)

            print("\n🔄 Sincronizando reloj con el servidor...")
            sync_exitosa = await self.sincronizar_reloj(rondas=5)
            
            if not sync_exitosa:
                print("⚠️  Advertencia: Sincronización falló, continuando sin sincronización")
            
            # 🆕 NUEVO: Solicitar colores disponibles antes de conectar
            print("\n🎨 Solicitando colores disponibles...")
            colores_disponibles = await self.solicitar_colores_disponibles()
            
            if not colores_disponibles:
                print("❌ Error: No se pudieron obtener colores disponibles")
                return False
            
            print(f"✅ Colores disponibles: {colores_disponibles}")
            
            # 🆕 NUEVO: Permitir al usuario elegir color
            color_elegido = await self.elegir_color(colores_disponibles)
            
            if not color_elegido:
                print("❌ Error: No se seleccionó ningún color")
                return False
            
            print(f"✅ Color seleccionado: {color_elegido}")
            
            # Enviar mensaje de conexión CON el color elegido
            mensaje = proto.mensaje_conectar(nombre, color_elegido)  # 🆕 Agregar color
            print(f"🔍 DEBUG: Enviando mensaje CONECTAR: {mensaje}")
            
            await self.enviar(mensaje)
            
            print(f"🔍 DEBUG: Mensaje CONECTAR enviado")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def solicitar_colores_disponibles(self):
        """Solicita al servidor la lista de colores disponibles"""
        try:
            # Enviar solicitud
            mensaje = proto.mensaje_solicitar_colores()
            await self.enviar(mensaje)
            
            # Esperar respuesta (con timeout)
            timeout = 5.0
            tiempo_inicio = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - tiempo_inicio) < timeout:
                try:
                    # Intentar obtener mensaje de la cola
                    mensaje = await asyncio.wait_for(
                        self.cola_mensajes.get(), 
                        timeout=0.5
                    )
                    
                    if mensaje.get("tipo") == proto.MSG_COLORES_DISPONIBLES:
                        colores = mensaje.get("colores", [])
                        return colores
                    else:
                        # Si no es el mensaje esperado, volver a poner en cola
                        await self.cola_mensajes.put(mensaje)
                        
                except asyncio.TimeoutError:
                    continue
            
            print("⚠️ Timeout esperando colores disponibles")
            return None
            
        except Exception as e:
            print(f"❌ Error solicitando colores: {e}")
            return None

    async def elegir_color(self, colores_disponibles):
        """
        Permite al usuario elegir un color de los disponibles.
        Puedes personalizar esto según tu interfaz (consola, GUI, etc.)
        """
        print("\n" + "="*50)
        print("🎨 SELECCIÓN DE COLOR")
        print("="*50)
        
        if not colores_disponibles:
            print("❌ No hay colores disponibles")
            return None
        
        # Mostrar colores con números
        for i, color in enumerate(colores_disponibles, 1):
            print(f"{i}. {color.upper()}")
        
        print("="*50)
        
        # Obtener selección del usuario
        while True:
            try:
                # Si estás usando una interfaz gráfica, aquí llamarías a tu método de GUI
                seleccion = input(f"Elige tu color (1-{len(colores_disponibles)}): ").strip()
                
                indice = int(seleccion) - 1
                
                if 0 <= indice < len(colores_disponibles):
                    color_elegido = colores_disponibles[indice]
                    return color_elegido
                else:
                    print(f"❌ Opción inválida. Elige entre 1 y {len(colores_disponibles)}")
                    
            except ValueError:
                print("❌ Entrada inválida. Ingresa un número.")
            except KeyboardInterrupt:
                print("\n❌ Selección cancelada")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")    
        


    async def recibir_mensajes(self):
        """Tarea que recibe mensajes del servidor constantemente"""
        print(f"🔍 DEBUG: recibir_mensajes() iniciado")
        try:
            async for mensaje_raw in self.websocket:
                print(f"🔍 DEBUG: Mensaje recibido del servidor: {mensaje_raw[:100]}")
                try:
                    if not mensaje_raw or not mensaje_raw.strip():
                        self.log_debug("Mensaje vacío recibido")
                        continue
                    
                    mensaje = json.loads(mensaje_raw)
                    print(f"🔍 DEBUG: Mensaje parseado: {mensaje}")
                    
                    # Agregar a la cola
                    await self.cola_mensajes.put(mensaje)
                    print(f"🔍 DEBUG: Mensaje agregado a cola")
                    
                except json.JSONDecodeError as e:
                    print(f"🔍 DEBUG: Error parseando JSON: {e}")
                except Exception as e:
                    print(f"🔍 DEBUG: Error procesando mensaje: {e}")
                    
        except websockets.exceptions.ConnectionClosedOK:
            print("\n🔴 Conexión cerrada por el servidor (OK)")
            self.conectado = False
        except websockets.exceptions.ConnectionClosed as e:
            print(f"\n🔴 Conexión perdida: {e.reason if hasattr(e, 'reason') else 'Sin razón'}")
            print(f"🔍 DEBUG: Código de cierre: {e.code if hasattr(e, 'code') else 'N/A'}")
            self.conectado = False
        except Exception as e:
            print(f"\n❌ Error inesperado en receptor: {e}")
            import traceback
            traceback.print_exc()
            self.conectado = False
    
    async def procesar_mensajes(self):
        """Procesa mensajes de la cola"""
        mensajes_procesados = 0
        while not self.cola_mensajes.empty() and mensajes_procesados < 20:
            try:
                mensaje = self.cola_mensajes.get_nowait()
                await self.manejar_mensaje(mensaje)
                mensajes_procesados += 1
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                self.log_debug(f"Error procesando mensaje: {e}")
    
    def resetear_estado_dados(self):
        """Resetea el estado de dados para un nuevo turno"""
        self.dados_lanzados = False
        self.ultimo_dado1 = 0
        self.ultimo_dado2 = 0
        self.ultima_suma = 0
        self.ultimo_es_doble = False
        self.esperando_dados = False
        self.esperando_movimiento = False
        self.dados_usados = []
        self.log_debug("🔄 Estado de dados reseteado para nuevo turno")
    
    async def manejar_mensaje(self, mensaje):
        """Maneja un mensaje recibido del servidor"""
        tipo = mensaje.get("tipo")
        self.log_debug(f"Procesando mensaje tipo: {tipo}")

        if tipo == proto.MSG_BIENVENIDA:
            self.mi_color = mensaje["color"]
            self.mi_id = mensaje["jugador_id"]
            print(f"\n🎨 Te asignaron el color: {self.mi_color.upper()}")
            print(f"👤 Tu ID: {self.mi_id}")

        elif tipo == proto.MSG_ESPERANDO:
            conectados = mensaje.get("conectados", 0)
            requeridos = mensaje.get("requeridos", proto.MIN_JUGADORES)
            self.conectados = conectados
            self.requeridos = requeridos
            print(f"\n⏳ Esperando jugadores... ({conectados}/{requeridos})")

        elif tipo == proto.MSG_INICIO_JUEGO:
            self.juego_iniciado = True
            self.jugadores = mensaje.get("jugadores", [])
            self.conectados = len(self.jugadores)
            print("\n" + "="*60)
            print("🎮 ¡EL JUEGO HA COMENZADO! 🎮".center(60))
            print("="*60)
            print("\n👥 Jugadores:")
            for j in self.jugadores:
                marca = "⭐" if j["color"] == self.mi_color else "  "
                print(f"{marca} {j['nombre']} ({j['color'].upper()})")
            print("="*60 + "\n")

        elif tipo == proto.MSG_TURNO:
            nombre = mensaje["nombre"]
            color = mensaje["color"]
            era_mi_turno_anterior = self.es_mi_turno
            self.es_mi_turno = (color == self.mi_color)

            if self.es_mi_turno:
                if not era_mi_turno_anterior:
                    self.log_debug("🔄 Nuevo turno - reseteando estado de dados")
                    self.resetear_estado_dados()
                else:
                    self.dados_lanzados = False
                    self.esperando_dados = False
                    self.esperando_movimiento = False
                    self.dados_usados = []
                    self.log_debug("🔄 Manteniendo turno por dobles - reseteando estado")
            else:
                self.esperando_dados = False
                self.esperando_movimiento = False

            print("\n" + "─"*60)
            if self.es_mi_turno:
                print(f"🎯 ES TU TURNO 🎯".center(60))
            else:
                print(f"⏳ Turno de {nombre} ({color.upper()})".center(60))
            print("─"*60)

        elif tipo == proto.MSG_DADOS:
            self.ultimo_dado1 = mensaje["dado1"]
            self.ultimo_dado2 = mensaje["dado2"]
            self.ultima_suma = mensaje["suma"]
            self.ultimo_es_doble = mensaje["es_doble"]
            self.dados_lanzados = True
            self.esperando_dados = False
            self.dados_usados = []

            if self.es_mi_turno:
                dobles_msg = "¡DOBLES! 🎉" if self.ultimo_es_doble else ""
                print(f"\n🎲 RESULTADO: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma} {dobles_msg}")

                if self.ultimo_es_doble:
                    todas_en_carcel = True
                    for jugador in self.jugadores:
                        if jugador["color"] == self.mi_color:
                            todas_en_carcel = all(f["estado"] == "BLOQUEADO" for f in jugador["fichas"])
                            break
                    
                    if todas_en_carcel:
                        print("\n🔓 ¡Sacaste dobles! Liberando todas las fichas de la cárcel...")
                        await self.enviar(proto.mensaje_sacar_todas())
                        return
                    else:
                        print("🔄 ¡Sacaste dobles! Puedes sacar una ficha de la cárcel y mantener tu turno.")
                else:
                    print("➡️ Sin dobles. Mueve una ficha y tu turno terminará.")

        elif tipo == proto.MSG_TABLERO:
            self.estado_tablero = mensaje
            if "jugadores" in mensaje:
                self.jugadores = mensaje["jugadores"]

        elif tipo == proto.MSG_MOVIMIENTO_OK:
            nombre = mensaje["nombre"]
            color = mensaje["color"]
            desde = mensaje["desde"]
            hasta = mensaje["hasta"]
            accion = mensaje.get("accion", "mover")

            if accion == "liberar_ficha":
                print(f"🔓 {nombre} ({color}) liberó ficha automáticamente → C{hasta + 1}")
            else:
                desde_str = "CÁRCEL" if desde == -1 else f"C{desde + 1}"
                print(f"✅ {nombre} ({color}) movió ficha de {desde_str} → C{hasta + 1}")

            if self.es_mi_turno:
                self.ultimo_movimiento_exitoso = True

            if self.ultimo_es_doble and self.es_mi_turno:
                self.dados_lanzados = False
                self.esperando_dados = False
                print("\n🎲 ¡Sacaste dobles! Puedes volver a lanzar los dados.")

            self.esperando_movimiento = False

        elif tipo == proto.MSG_CAPTURA:
            capturado = mensaje.get("capturado", {})
            quien = capturado.get("nombre", mensaje.get("nombre", "Desconocido"))
            color = capturado.get("color", mensaje.get("color", "??"))
            ficha_id = capturado.get("ficha_id", mensaje.get("ficha_id", -1))
            try:
                print(f"\n⚠️ {quien} ({color}) ha sido CAPTURADO: Ficha {ficha_id + 1} enviada a cárcel")
            except Exception:
                print(f"\n⚠️ {quien} ({color}) ha sido CAPTURADO y una ficha fue enviada a cárcel")

        elif tipo == proto.MSG_ERROR:
            error_msg = mensaje.get('mensaje', 'Error desconocido')
            print(f"\n❌ Error: {error_msg}")
            self.esperando_dados = False
            self.esperando_movimiento = False

        elif tipo == proto.MSG_VICTORIA:
            ganador = mensaje["ganador"]
            color = mensaje["color"]
            print("\n" + "🏆"*30)
            if color == self.mi_color:
                print("🎉 ¡¡¡HAS GANADO!!! 🎉".center(60))
            else:
                print(f"🏆 {ganador} ({color.upper()}) HA GANADO 🏆".center(60))
            print("🏆"*30 + "\n")
            self.running = False

        elif tipo == proto.MSG_JUGADOR_DESCONECTADO:
            nombre = mensaje.get("nombre", "Desconocido")
            color = mensaje.get("color", "??")
            print(f"\n⚠️ {nombre} ({color}) se ha desconectado")

        # ⭐ NUEVO: Handlers para determinación de turnos
        elif tipo == proto.MSG_DETERMINACION_INICIO:
            self.en_determinacion = True
            self.ya_lance_en_determinacion = False
            self.estoy_en_desempate = False
            mensaje_texto = mensaje.get("mensaje", "Determinando orden de turnos...")
            jugador_actual = mensaje.get("jugador_actual", "")
            
            print("\n" + "="*60)
            print("🎲 DETERMINACIÓN DE TURNOS 🎲".center(60))
            print("="*60)
            print(f"\n{mensaje_texto}")
            print("\n💡 Los jugadores lanzarán los dados en orden para determinar quién empieza primero.")
            print("   El jugador con la suma más alta comenzará el juego.")
            
            # Si no hay jugador_actual, asignar al jugador con ID 0 (primer jugador)
            if not jugador_actual and self.mi_id == 0:
                jugador_actual = self.mi_nombre
            
            # Mostrar de quién es el turno
            if jugador_actual == self.mi_nombre:
                print("\n🎯 ES TU TURNO PARA LANZAR")
                self.mi_turno_determinado = True
            else:
                # Si no hay jugador_actual, mostrar mensaje genérico
                msg = f"\n⏳ Esperando a que {jugador_actual} lance los dados..." if jugador_actual else "\n⏳ Esperando turno..."
                print(msg)
                self.mi_turno_determinado = False
            
            print("="*60 + "\n")
        
        elif tipo == proto.MSG_DETERMINACION_RESULTADO:
            nombre = mensaje.get("nombre")
            color = mensaje.get("color")
            dado1 = mensaje.get("dado1")
            dado2 = mensaje.get("dado2")
            suma = mensaje.get("suma")
            siguiente = mensaje.get("siguiente", "")
            
            es_mi_tirada = (color == self.mi_color)
            
            if es_mi_tirada:
                self.ya_lance_en_determinacion = True
                print(f"\n🎲 Tu tirada: [{dado1}] [{dado2}] = {suma}")
            else:
                print(f"\n📊 {nombre} ({color}): [{dado1}] [{dado2}] = {suma}")
            
            # Si hay un siguiente jugador, actualizar los estados
            if siguiente:
                self.mi_turno_determinado = (siguiente == self.mi_nombre)
                if self.mi_turno_determinado:
                    print("\n🎯 ES TU TURNO PARA LANZAR")
                    print("="*60 + "\n")
                else:
                    print(f"\n⏳ Esperando a que {siguiente} lance los dados...")
                    print("="*60 + "\n")
        
        elif tipo == proto.MSG_DETERMINACION_EMPATE:
            jugadores = mensaje.get("jugadores", [])
            valor = mensaje.get("valor")
            mensaje_texto = mensaje.get("mensaje", "")
            
            print("\n" + "⚔️ "*15)
            print(f"EMPATE CON {valor} PUNTOS".center(60))
            print("⚔️ "*15)
            print(f"\n{mensaje_texto}")
            print("\nJugadores empatados que deben volver a tirar:")
            
            # Verificar si estoy en el desempate
            self.estoy_en_desempate = False
            for j in jugadores:
                marca = ""
                if j['color'] == self.mi_color:
                    marca = "👉 "
                    self.estoy_en_desempate = True
                    self.ya_lance_en_determinacion = False  # Permitir tirar de nuevo
                print(f"{marca}   • {j['nombre']} ({j['color']}) - {j['suma']} puntos")
            
            if self.estoy_en_desempate:
                print("\n💡 Lanza los dados nuevamente para desempatar.")
            print("="*60 + "\n")
        
        elif tipo == proto.MSG_DETERMINACION_GANADOR:
            ganador = mensaje.get("ganador", {})
            orden = mensaje.get("orden", [])
            mensaje_texto = mensaje.get("mensaje", "")
            
            print("\n" + "🏆"*30)
            print("DETERMINACIÓN COMPLETADA".center(60))
            print("🏆"*30)
            
            print(f"\n{mensaje_texto}")
            print(f"\n🥇 Ganador: {ganador['nombre']} ({ganador['color'].upper()})")
            
            print("\n📋 Orden de turnos establecido:")
            for i, j in enumerate(orden, 1):
                marca = "👉" if j['color'] == self.mi_color else "  "
                print(f"{marca} {i}. {j['nombre']} ({j['color'].upper()})")
            
            print("\n🎮 El juego comenzará en breve...")
            print("="*60 + "\n")
            
            # Resetear flags de determinación
            self.en_determinacion = False
            self.ya_lance_en_determinacion = False
            self.estoy_en_desempate = False

        elif tipo == proto.MSG_PREMIO_TRES_DOBLES:
            fichas_elegibles = mensaje.get("fichas_elegibles", [])
            mensaje_texto = mensaje.get("mensaje", "")
            
            print("\n" + "🏆"*30)
            print("¡PREMIO DE 3 DOBLES!".center(60))
            print("🏆"*30)
            print(f"\n{mensaje_texto}")
            print("\n📋 Fichas elegibles para enviar a META:")
            
            for ficha in fichas_elegibles:
                ficha_id = ficha['id']
                posicion = ficha.get('posicion', '?')
                estado = ficha.get('estado', '')
                
                if estado == "EN_JUEGO":
                    print(f"   {ficha_id + 1}. Ficha en casilla {posicion + 1}")
                else:
                    print(f"   {ficha_id + 1}. Ficha (estado: {estado})")
            
            print("\n" + "="*60)
            
            # Solicitar elección al usuario
            try:
                loop = asyncio.get_event_loop()
                seleccion = await loop.run_in_executor(
                    None,
                    input,
                    f"\n🏆 Elige una ficha para enviar a META (1-{len(fichas_elegibles)}): "
                )
                ficha_num = int(seleccion)
                
                if 1 <= ficha_num <= len(fichas_elegibles):
                    ficha_elegida = fichas_elegibles[ficha_num - 1]
                    ficha_id = ficha_elegida['id']
                    
                    print(f"\n✅ Enviando ficha {ficha_id + 1} a META...")
                    await self.enviar(proto.mensaje_elegir_ficha_premio(ficha_id))
                    
                    # Esperar respuesta
                    await asyncio.sleep(1.0)
                    await self.procesar_mensajes()
                else:
                    print("⚠️ Número de ficha inválido")
                    
            except ValueError:
                print("⚠️ Entrada inválida")
            except Exception as e:
                print(f"❌ Error eligiendo ficha: {e}")
        
        elif tipo == proto.MSG_INFO:
            info_text = mensaje.get('mensaje', '')
            print(f"\nℹ️ {info_text}")

            es_admin_flag = mensaje.get("es_admin", None)
            
            # 🆕 AGREGAR DEBUG AQUÍ
            print(f"🔍 DEBUG INFO: es_admin_flag = {es_admin_flag}")
            print(f"🔍 DEBUG INFO: self.es_admin ANTES = {self.es_admin}")
            
            if es_admin_flag is not None:
                self.es_admin = bool(es_admin_flag)
                print(f"🔍 DEBUG INFO: self.es_admin DESPUÉS = {self.es_admin}")
                if self.es_admin:
                    self.log_debug("🔑 Marca local: soy admin (flag es_admin True)")
                else:
                    self.log_debug("🔑 Marca local: NO soy admin (flag es_admin False)")
    
    async def enviar(self, mensaje):
        """Envía un mensaje al servidor"""
        try:
            data = json.dumps(mensaje, ensure_ascii=False)
            await self.websocket.send(data)
            self.log_debug(f"Mensaje enviado: {mensaje}")
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            self.conectado = False
    
    async def esperar_respuesta_dados(self, timeout=5.0):
        """Espera específicamente la respuesta de dados"""
        tiempo_inicio = time.time()
        self.esperando_dados = True
        
        print("⏳ Esperando resultado de dados...")
        
        while self.esperando_dados and (time.time() - tiempo_inicio) < timeout:
            await self.procesar_mensajes()
            await asyncio.sleep(0.1)
            
            if int((time.time() - tiempo_inicio) * 10) % 10 == 0:
                print(".", end="", flush=True)
        
        if self.esperando_dados:
            print(f"\n⚠️ Timeout esperando dados ({timeout}s)")
            self.esperando_dados = False
            return False
        
        return True
    
    async def esperar_respuesta_movimiento(self, timeout=3.0):
        """Espera respuesta de movimiento"""
        tiempo_inicio = time.time()
        self.esperando_movimiento = True
        self.ultimo_movimiento_exitoso = False
        
        while self.esperando_movimiento and (time.time() - tiempo_inicio) < timeout:
            await self.procesar_mensajes()
            await asyncio.sleep(0.1)
        
        if self.esperando_movimiento:
            print(f"\n⚠️ Timeout esperando respuesta de movimiento")
            self.esperando_movimiento = False
            return False
        
        return self.ultimo_movimiento_exitoso
    
    def mostrar_estado_dados(self):
        """Muestra el estado actual de los dados"""
        if self.dados_lanzados and self.es_mi_turno:
            dobles_info = " ¡DOBLES!" if self.ultimo_es_doble else ""
            print(f"🎲 Última tirada: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}{dobles_info}")
        else:
            print("🎲 No se han lanzado dados en este turno")
    
    def mostrar_mis_fichas(self):
        """Muestra las fichas del jugador actual"""
        if not self.estado_tablero or "jugadores" not in self.estado_tablero:
            print("⚠️ No hay información del tablero disponible")
            return
        
        mi_info = None
        for jugador in self.estado_tablero["jugadores"]:
            if jugador["color"] == self.mi_color:
                mi_info = jugador
                break
        
        if not mi_info:
            print("⚠️ No se encontró tu información")
            return
        
        print("\n" + "─"*60)
        print(f"🎮 TUS FICHAS ({self.mi_color.upper()})".center(60))
        print("─"*60)
        
        fichas_bloqueadas = []
        fichas_en_juego = []
        fichas_en_camino_meta = []
        fichas_en_meta = []
        
        for ficha in mi_info["fichas"]:
            if ficha["estado"] == "BLOQUEADO":
                fichas_bloqueadas.append(ficha)
            elif ficha["estado"] == "EN_JUEGO":
                fichas_en_juego.append(ficha)
            elif ficha["estado"] == "CAMINO_META":
                fichas_en_camino_meta.append(ficha)
            elif ficha["estado"] == "META":
                fichas_en_meta.append(ficha)
        
        print("🔒 FICHAS EN CÁRCEL:")
        if fichas_bloqueadas:
            for ficha in fichas_bloqueadas:
                print(f"  └─ Ficha {ficha['id'] + 1}")
        else:
            print("  └─ Ninguna")
        
        print("\n🎮 FICHAS EN JUEGO:")
        if fichas_en_juego:
            for ficha in fichas_en_juego:
                futura_pos = ficha['posicion'] + self.ultima_suma if self.dados_lanzados and self.es_mi_turno else "?"
                movimiento_info = ""
                if self.dados_lanzados and self.es_mi_turno:
                    if isinstance(futura_pos, int):
                        if futura_pos >= 68:
                            futura_pos = futura_pos - 68
                        movimiento_info = f" → C{futura_pos + 1}"
                print(f"  └─ Ficha {ficha['id'] + 1}: C{ficha['posicion'] + 1}{movimiento_info}")
        else:
            print("  └─ Ninguna")
            
        print("\n🎯 FICHAS EN CAMINO A META:")
        if fichas_en_camino_meta:
            for ficha in fichas_en_camino_meta:
                casilla_actual = f"s{self.mi_color[0]}{ficha['posicion_meta'] + 1}"
                print(f"  └─ Ficha {ficha['id'] + 1}: {casilla_actual}")
        else:
            print("  └─ Ninguna")
        
        print("\n🏁 FICHAS EN META:")
        if fichas_en_meta:
            for ficha in fichas_en_meta:
                print(f"  └─ Ficha {ficha['id'] + 1}")
        else:
            print("  └─ Ninguna")
        
        print(f"\n📊 Total: 🔒{len(fichas_bloqueadas)} | 🎮{len(fichas_en_juego)} | 🏁{len(fichas_en_meta)}")
        print("─"*60)
    
    def mostrar_tablero_completo(self):
        """Muestra el estado completo del juego"""
        if not self.estado_tablero or "jugadores" not in self.estado_tablero:
            print("⚠️ No hay información del tablero disponible")
            return
        
        print("\n" + "="*60)
        print("📊 ESTADO COMPLETO DEL JUEGO".center(60))
        print("="*60)
        
        if hasattr(self, 'jugadores') and self.jugadores:
            turno_actual = self.estado_tablero.get("turno_actual", 0)
            if turno_actual < len(self.jugadores):
                jugador_turno = self.jugadores[turno_actual]
                print(f"🎯 Turno actual: {jugador_turno['nombre']} ({jugador_turno['color'].upper()})")
        
        if self.dados_lanzados and self.es_mi_turno:
            print(f"🎲 Últimos dados: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}")
            if self.ultimo_es_doble:
                dobles_consecutivos = self.estado_tablero.get("dobles_consecutivos", 0)
                print(f"🔄 Dobles consecutivos: {dobles_consecutivos}")
        
        print("\n👥 JUGADORES:")
        
        for jugador in self.estado_tablero["jugadores"]:
            marca = "⭐" if jugador["color"] == self.mi_color else "  "
            print(f"\n{marca} {jugador['nombre']} ({jugador['color'].upper()}):")
            print(f"   🔒 En cárcel: {jugador['bloqueadas']}")
            print(f"   🎮 En juego: {jugador['en_juego']}")
            print(f"   🏁 En meta: {jugador['en_meta']}")
            
            fichas_en_juego = [f for f in jugador["fichas"] if f["estado"] == "EN_JUEGO"]
            if fichas_en_juego:
                posiciones = [f"C{f['posicion'] + 1}" for f in fichas_en_juego]
                print(f"   📍 Posiciones: {', '.join(posiciones)}")
        
        print("="*60)
    
    def mostrar_tablero_visual(self):
        """Muestra el tablero de forma visual"""
        if not self.estado_tablero or "jugadores" not in self.estado_tablero:
            print("⚠️ No hay información del tablero disponible")
            return
        
        print("\n" + "="*80)
        print("🎲 TABLERO DE PARCHÍS 🎲".center(80))
        print("="*80)
        
        if hasattr(self, 'jugadores') and self.jugadores:
            turno_actual = self.estado_tablero.get("turno_actual", 0)
            if turno_actual < len(self.jugadores):
                jugador_actual = self.jugadores[turno_actual]
                turno_info = f"🎯 Turno de: {jugador_actual['nombre']} ({jugador_actual['color'].upper()})"
            else:
                turno_info = "🎯 Turno: Determinando..."
        else:
            turno_info = "🎯 Turno: Determinando..."
        
        print(turno_info.center(80))
        
        if self.dados_lanzados and self.es_mi_turno:
            dados_info = f"🎲 Dados: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}"
            if self.ultimo_es_doble:
                dados_info += " ¡DOBLES!"
            print(dados_info.center(80))
        
        print("="*80)
        
        posiciones_fichas = {}
        colores_map = {"rojo": "R", "azul": "A", "amarillo": "Am", "verde": "V"}
        
        for jugador in self.estado_tablero["jugadores"]:
            color_inicial = colores_map.get(jugador["color"], jugador["color"][0].upper())
            for ficha in jugador["fichas"]:
                if ficha["estado"] == "EN_JUEGO":
                    pos = ficha["posicion"]
                    if pos >= 0:
                        if pos not in posiciones_fichas:
                            posiciones_fichas[pos] = []
                        posiciones_fichas[pos].append(f"{color_inicial}{ficha['id']+1}")
        
        total_casillas = 68
        casillas_por_fila = 8
        
        for fila in range(0, total_casillas, casillas_por_fila):
            print(f"\n📍 Casillas {fila + 1} a {min(fila + casillas_por_fila, total_casillas)}:")
            
            header = ""
            for i in range(fila, min(fila + casillas_por_fila, total_casillas)):
                header += f"{i+1:3d} "
            print(f"     {header}")
            
            content = ""
            for i in range(fila, min(fila + casillas_por_fila, total_casillas)):
                fichas_aqui = posiciones_fichas.get(i, [])
                if fichas_aqui:
                    fichas_str = fichas_aqui[0][:3]
                else:
                    fichas_str = "---"
                content += f"{fichas_str:>3s} "
            print(f"     {content}")
        
        print("\n" + "-"*80)
        print("LEYENDA: R=Rojo, A=Azul, Am=Amarillo, V=Verde (número = ID de ficha)")
        print("ESTADÍSTICAS:")
        
        for jugador in self.estado_tablero["jugadores"]:
            marca = "⭐" if jugador["color"] == self.mi_color else "  "
            print(f"{marca} {jugador['nombre']} ({jugador['color'].upper()}): "
                  f"🔒{jugador['bloqueadas']} | 🎮{jugador['en_juego']} | 🏁{jugador['en_meta']}")
        
        print("="*80)
    
    async def menu_turno(self):
        """Muestra el menú principal durante el turno"""
        print(f"\n{'='*60}")
        print(f"🎯 TU TURNO - {self.mi_nombre} ({self.mi_color.upper()})".center(60))
        print(f"{'='*60}")
        
        self.mostrar_estado_dados()
        
        opciones = []
        
        if not self.dados_lanzados:
            opciones = [
                "🎲 Lanzar dados",
                "👀 Ver mis fichas", 
                "📊 Ver tablero completo",
                "🎯 Ver tablero visual",
                "🚪 Salir"
            ]
        else:
            todas_en_carcel = True
            fichas_en_juego = 0
            for jugador in self.jugadores:
                if jugador["color"] == self.mi_color:
                    todas_en_carcel = all(f["estado"] == "BLOQUEADO" for f in jugador["fichas"])
                    fichas_en_juego = sum(1 for f in jugador["fichas"] 
                                        if f["estado"] in ["EN_JUEGO", "CAMINO_META"])
                    break
            
            if self.ultimo_es_doble and todas_en_carcel:
                print("\n🔓 Liberando todas las fichas automáticamente...")
                await self.enviar(proto.mensaje_sacar_todas())
                return "0", []
            elif self.ultimo_es_doble:
                opciones = [
                    "🔓 Sacar ficha de la cárcel" if not todas_en_carcel else None,
                    "🎮 Mover ficha en juego" if fichas_en_juego > 0 else None,
                    "👀 Ver mis fichas",
                    "📊 Ver tablero completo",
                    "🎯 Ver tablero visual",
                    "🚪 Salir"
                ]
                opciones = [opt for opt in opciones if opt is not None]
            else:
                opciones = [
                    "🎮 Mover ficha en juego" if fichas_en_juego > 0 else None,
                    "👀 Ver mis fichas",
                    "📊 Ver tablero completo",
                    "🎯 Ver tablero visual",
                    "🚪 Salir"
                ]
                opciones = [opt for opt in opciones if opt is not None]
        
        print("\n¿Qué deseas hacer?")
        for i, opcion in enumerate(opciones, 1):
            print(f"{i}. {opcion}")
        
        try:
            # Usar input bloqueante normal (asyncio lo maneja)
            loop = asyncio.get_event_loop()
            opcion = await loop.run_in_executor(None, input, f"\nOpción (1-{len(opciones)}): ")
            return opcion.strip(), opciones
        except:
            return "0", opciones

    async def ejecutar(self):
        """Loop principal del cliente"""
        
        # 🆕 VERIFICAR SI YA ESTÁ CONECTADO
        if not self.conectado:
            # Solo mostrar banner y pedir nombre si NO está conectado
            print("\n" + "="*60)
            print("🎲 CLIENTE DE PARCHÍS 🎲".center(60))
            print("="*60)

            nombre = input("Ingresa tu nombre: ").strip()
            if not nombre:
                nombre = f"Jugador_{int(time.time()) % 1000}"

            if not await self.conectar(nombre):
                return
        else:
            # Ya está conectado desde hybrid.py - solo mostrar confirmación
            print(f"\n✅ Sesión activa como {self.mi_nombre}")

        print("\n⏳ Esperando que el juego comience...")

        if not hasattr(self, "_last_conectados"):
            self._last_conectados = None
        if not hasattr(self, "_last_requeridos"):
            self._last_requeridos = None
        if not hasattr(self, "_last_missing"):
            self._last_missing = None

        # Warm-up
        for _ in range(12):
            await self.procesar_mensajes()
            if getattr(self, "conectados", 0) > 0:
                break
            await asyncio.sleep(0.03)

        # Bucle PRE-JUEGO
        try:
            # ⭐ IMPORTANTE: Salir del loop cuando inicia la determinación O el juego
            while self.running and self.conectado and not self.juego_iniciado and not self.en_determinacion:
                await self.procesar_mensajes()

                conectados = getattr(self, "conectados", 0)
                requeridos = getattr(self, "requeridos", proto.MIN_JUGADORES)

                # 🔧 ARREGLAR: Mostrar número correcto de jugadores
                if (conectados != self._last_conectados) or (requeridos != self._last_requeridos):
                    print(f"\nConectados: {conectados} / {requeridos}")  # ← CAMBIADO
                    self._last_conectados = conectados
                    self._last_requeridos = requeridos

                if getattr(self, "es_admin", False):
                    if conectados < proto.MIN_JUGADORES:
                        faltan = proto.MIN_JUGADORES - conectados
                        if self._last_missing != faltan:
                            print(f"(No puedes iniciar aún: faltan {faltan} jugador(es))")
                            self._last_missing = faltan
                        await asyncio.sleep(0.5)
                        continue

                    self._last_missing = None
                    
                    # 🆕 MOSTRAR PROMPT CADA VEZ QUE HAY SUFICIENTES JUGADORES
                    print(f"\n✅ Suficientes jugadores conectados ({conectados}/{requeridos})")
                    
                    try:
                        loop = asyncio.get_event_loop()
                        cmd = await loop.run_in_executor(
                            None, 
                            input, 
                            "🚀 Escribe 'start' para iniciar la partida o Enter para refrescar: "
                        )
                        cmd = cmd.strip().lower()
                    except KeyboardInterrupt:
                        print("\n\n⚠️ Interrupción por teclado durante espera previa...")
                        await self.desconectar()
                        return
                    except Exception as e:
                        print(f"⚠️ Error leyendo input: {e}")
                        await asyncio.sleep(0.5)
                        continue

                    if cmd == "start":
                        print("🔔 Enviando solicitud de inicio (MSG_LISTO) al servidor...")
                        try:
                            await self.enviar(proto.mensaje_listo())
                            print("✅ MSG_LISTO enviado correctamente")
                            
                            # Esperar a que llegue MSG_DETERMINACION_INICIO
                            await asyncio.sleep(0.3)
                            await self.procesar_mensajes()
                            
                            # Salir del loop de admin para entrar al loop de determinación
                            break
                            
                        except Exception as e:
                            print(f"❌ Error enviando MSG_LISTO: {e}")
                        continue

                    await asyncio.sleep(0.2)
                else:
                    await asyncio.sleep(0.5)

            if not self.running or not self.conectado:
                await self.desconectar()
                return

        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupción por teclado durante espera previa...")
            await self.desconectar()
            return
        except Exception as e:
            print(f"\n❌ Error en fase previa al juego: {e}")
            try:
                await self.desconectar()
            except Exception:
                pass
            return

        # ⭐ NUEVO: Loop de determinación de turnos
        try:
            # Variable para controlar si ya mostramos el prompt
            prompt_mostrado = False
            
            while self.running and self.conectado and self.en_determinacion:
                await self.procesar_mensajes()
                
                # Si no es mi turno o ya lancé, solo esperar
                if not self.mi_turno_determinado or self.ya_lance_en_determinacion:
                    prompt_mostrado = False  # Resetear para la siguiente ronda
                    await asyncio.sleep(0.3)
                    continue
                
                # Si estoy en desempate pero no soy parte, esperar
                if self.jugadores_en_desempate and not self.estoy_en_desempate:
                    prompt_mostrado = False
                    await asyncio.sleep(0.3)
                    continue
                
                # Mostrar prompt solo una vez
                if not prompt_mostrado:
                    print("\n" + "="*60)
                    print("💡 ES TU TURNO PARA LANZAR LOS DADOS".center(60))
                    print("="*60)
                    print("\n📋 Comandos disponibles:")
                    print("   • 'lanzar' o 'l' - Lanzar los dados")
                    print("="*60)
                    prompt_mostrado = True
                
                try:
                    loop = asyncio.get_event_loop()
                    cmd = await loop.run_in_executor(
                        None,
                        input,
                        "\n🎲 Comando: "
                    )
                    cmd = cmd.strip().lower()
                    
                    if cmd in ['lanzar', 'l']:
                        # Generar dados en el cliente
                        import random
                        dado1 = random.randint(1, 6)
                        dado2 = random.randint(1, 6)
                        
                        print(f"\n🎲 Lanzando dados: [{dado1}] [{dado2}]...")
                        await self.enviar(proto.mensaje_determinacion_tirada(dado1, dado2))
                        
                        # Marcar que ya lancé
                        self.ya_lance_en_determinacion = True
                        prompt_mostrado = False
                        
                        # Esperar un poco para procesar la respuesta
                        await asyncio.sleep(0.5)
                    else:
                        print("⚠️ Comando no reconocido. Usa 'lanzar' o 'l'")
                        # No resetear prompt_mostrado para que no se repita el encabezado
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️ Interrupción durante determinación...")
                    await self.desconectar()
                    return
                except Exception as e:
                    print(f"❌ Error en determinación: {e}")
                    await asyncio.sleep(0.5)
            
            if not self.running or not self.conectado:
                await self.desconectar()
                return
                
        except Exception as e:
            print(f"\n❌ Error en fase de determinación: {e}")
            try:
                await self.desconectar()
            except Exception:
                pass
            return

        # Loop principal del juego (turnos)
        try:
            while self.running and self.conectado:
                await self.procesar_mensajes()

                if not self.juego_iniciado or not self.es_mi_turno:
                    await asyncio.sleep(0.2)
                    continue

                opcion, opciones = await self.menu_turno()

                try:
                    if opcion.lower() in ['debug3', 'd3', 'forzar3dobles']:
                        print("\n🔧 Forzando 3 dobles consecutivos (debug)...")
                        try:
                            await self.enviar(proto.mensaje_debug_forzar_tres_dobles())
                            print("✅ Mensaje de forzar 3 dobles enviado")
                            await asyncio.sleep(1.0)
                            await self.procesar_mensajes()
                        except Exception as e:
                            print(f"❌ Error enviando mensaje de forzar 3 dobles: {e}")
                        continue

                    opcion_num = int(opcion)
                    if opcion_num < 1 or opcion_num > len(opciones):
                        print("⚠️ Opción no válida")
                        continue

                    accion = opciones[opcion_num - 1]

                    if "Lanzar dados" in accion:
                        print("\n🎲 Lanzando dados...")
                        await self.enviar(proto.mensaje_lanzar_dados())
                        if await self.esperar_respuesta_dados():
                            print("✅ Dados recibidos correctamente")
                        else:
                            print("❌ Error recibiendo dados")

                    elif "Sacar ficha" in accion:
                        print("\n🔓 Intentando sacar ficha de la cárcel...")
                        await self.enviar(proto.mensaje_sacar_carcel())
                        await self.esperar_respuesta_movimiento()

                    elif "Mover ficha en juego" in accion:
                        await self.elegir_y_mover_ficha()

                    elif "Ver mis fichas" in accion:
                        self.mostrar_mis_fichas()
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, input, "\nPresiona Enter para continuar...")

                    elif "Ver tablero completo" in accion:
                        self.mostrar_tablero_completo()
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, input, "\nPresiona Enter para continuar...")

                    elif "Ver tablero visual" in accion:
                        self.mostrar_tablero_visual()
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, input, "\nPresiona Enter para continuar...")

                    elif "Salir" in accion:
                        print("\n👋 Saliendo del juego...")
                        break

                except ValueError:
                    print("⚠️ Ingresa un número válido")
                    continue
                except Exception as e:
                    print(f"❌ Error procesando opción: {e}")
                    continue

        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupción recibida...")
        except Exception as e:
            print(f"\n❌ Error inesperado en el loop principal: {e}")
        finally:
            await self.desconectar()


    async def elegir_y_mover_ficha(self):
        """Permite al jugador elegir qué ficha mover"""
        print("\n" + "─"*50)
        print("🎮 MOVER FICHA".center(50))
        print("─"*50)
        
        self.mostrar_mis_fichas()
        
        try:
            loop = asyncio.get_event_loop()
            ficha_input = await loop.run_in_executor(
                None, 
                input, 
                f"\n¿Qué ficha deseas mover? (1-{proto.FICHAS_POR_JUGADOR}): "
            )
            ficha_num = int(ficha_input)
            
            if not (1 <= ficha_num <= proto.FICHAS_POR_JUGADOR):
                print(f"⚠️ Número de ficha inválido (debe ser 1-{proto.FICHAS_POR_JUGADOR})")
                return
                
            dado_elegido = 3
            
            if len(self.dados_usados) == 1:
                dado_elegido = 2 if self.dados_usados[0] == 1 else 1
                valor_dado = self.ultimo_dado2 if self.dados_usados[0] == 1 else self.ultimo_dado1
                print(f"\n🎲 Usando el dado restante ({valor_dado})")
                
                print(f"\n🎮 Moviendo ficha {ficha_num}...")
                await self.enviar(proto.mensaje_mover_ficha(ficha_num - 1, dado_elegido))
                movimiento_exitoso = await self.esperar_respuesta_movimiento()
                
                if not self.es_mi_turno:
                    return
                
                if movimiento_exitoso:
                    self.dados_usados.append(dado_elegido)
                
                return
            
            print(f"\nDados disponibles: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}")
            print(f"1. Usar primer dado ({self.ultimo_dado1})")
            print(f"2. Usar segundo dado ({self.ultimo_dado2})")
            print(f"3. Usar suma de dados ({self.ultima_suma})")
            
            try:
                opcion_input = await loop.run_in_executor(None, input, "Elige una opción (1-3): ")
                opcion = int(opcion_input)
                if opcion not in [1, 2, 3]:
                    print("⚠️ Opción inválida")
                    return
                dado_elegido = opcion
            except ValueError:
                print("⚠️ Entrada inválida")
                return
            
            print(f"\n🎮 Moviendo ficha {ficha_num}...")
            await self.enviar(proto.mensaje_mover_ficha(ficha_num - 1, dado_elegido))
            movimiento_exitoso = await self.esperar_respuesta_movimiento()
            
            if not self.es_mi_turno:
                return
            
            if movimiento_exitoso and dado_elegido in [1, 2]:
                self.dados_usados.append(dado_elegido)
                print("\n🎲 Moviendo otra ficha con el dado restante...")
                await self.elegir_y_mover_ficha()
            
        except ValueError:
            print("⚠️ Ingresa un número válido")
    
    async def desconectar(self):
        """Desconecta del servidor"""
        self.running = False
        self.conectado = False
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
        print("\n👋 Desconectado del servidor")


async def main():
    print("🎲 CLIENTE DE PARCHÍS DISTRIBUIDO 🎲")
    print("=" * 50)
    
    # Configuración del servidor
    SERVIDOR_IP = input("IP del servidor (default: localhost): ").strip() or "localhost"
    
    try:
        SERVIDOR_PUERTO = int(input("Puerto del servidor (default: 8001): ").strip() or "8001")
    except:
        SERVIDOR_PUERTO = 8001
    
    cliente = ParchisClient(SERVIDOR_IP, SERVIDOR_PUERTO)
    
    try:
        await cliente.ejecutar()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupción recibida...")
        await cliente.desconectar()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        await cliente.desconectar()


if __name__ == "__main__":
    asyncio.run(main())
