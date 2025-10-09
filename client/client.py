import socket
import threading
import json
import sys
import queue
import time
import protocol as proto

class ParchisClient:
    def __init__(self, servidor_ip, servidor_puerto):
        self.servidor_ip = servidor_ip
        self.servidor_puerto = servidor_puerto
        self.socket = None
        self.conectado = False
        self.running = False
        
        # Información del jugador
        self.mi_nombre = ""
        self.mi_color = ""
        self.mi_id = -1
        
        # Estado del juego
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
        
        # Cola de mensajes para el hilo principal
        self.cola_mensajes = queue.Queue()
        
        # Control de flujo mejorado
        self.esperando_dados = False
        self.esperando_movimiento = False
        
        # Debug
        self.debug = False
        
    def log_debug(self, mensaje):
        """Logging para debug"""
        if self.debug:
            print(f"[DEBUG] {mensaje}")
    
    def conectar(self, nombre):
        """Conecta al servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.servidor_ip, self.servidor_puerto))
            self.conectado = True
            self.running = True
            self.mi_nombre = nombre
            
            print(f"\n✅ Conectado al servidor {self.servidor_ip}:{self.servidor_puerto}")
            
            # Enviar mensaje de conexión
            self.enviar(proto.mensaje_conectar(nombre))
            
            # Iniciar hilo receptor
            receptor_thread = threading.Thread(target=self.recibir_mensajes)
            receptor_thread.daemon = True
            receptor_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            return False
    
    def recibir_mensajes(self):
        """Hilo que recibe mensajes del servidor constantemente"""
        buffer = ""
        
        while self.running and self.conectado:
            try:
                # Recibir datos del servidor
                data = self.socket.recv(4096)
                if not data:
                    print("\n🔴 Conexión perdida con el servidor")
                    self.conectado = False
                    break
                
                # Decodificar datos
                try:
                    buffer += data.decode('utf-8')
                except UnicodeDecodeError as e:
                    self.log_debug(f"Error de decodificación: {e}")
                    continue
                
                self.log_debug(f"Buffer recibido: {buffer[:100]}...")
                
                # Procesar todos los mensajes completos en el buffer
                while buffer.strip():
                    try:
                        # Intentar decodificar un JSON
                        mensaje, idx = json.JSONDecoder().raw_decode(buffer)
                        self.log_debug(f"Mensaje recibido: {mensaje}")
                        
                        # Agregar a la cola
                        self.cola_mensajes.put(mensaje)
                        
                        # Remover el mensaje procesado del buffer
                        buffer = buffer[idx:].lstrip()
                        
                    except json.JSONDecodeError as e:
                        self.log_debug(f"JSON incompleto, esperando más datos: {e}")
                        break
                        
            except socket.error as e:
                if self.running:
                    print(f"\n❌ Error de socket: {e}")
                    self.conectado = False
                break
            except Exception as e:
                if self.running:
                    print(f"\n❌ Error inesperado en receptor: {e}")
                    self.conectado = False
                break
    
    def procesar_mensajes(self):
        """Procesa mensajes de la cola (en hilo principal)"""
        mensajes_procesados = 0
        while not self.cola_mensajes.empty() and mensajes_procesados < 20:
            try:
                mensaje = self.cola_mensajes.get_nowait()
                self.manejar_mensaje(mensaje)
                mensajes_procesados += 1
            except queue.Empty:
                break
            except Exception as e:
                self.log_debug(f"Error procesando mensaje: {e}")
    
    def resetear_estado_dados(self):
        """⭐ NUEVO: Resetea el estado de dados para un nuevo turno"""
        self.dados_lanzados = False
        self.ultimo_dado1 = 0
        self.ultimo_dado2 = 0
        self.ultima_suma = 0
        self.ultimo_es_doble = False
        self.esperando_dados = False
        self.esperando_movimiento = False
        self.log_debug("🔄 Estado de dados reseteado para nuevo turno")
    
    def manejar_mensaje(self, mensaje):
        """Maneja un mensaje recibido del servidor"""
        tipo = mensaje.get("tipo")
        self.log_debug(f"Procesando mensaje tipo: {tipo}")
        
        if tipo == proto.MSG_BIENVENIDA:
            self.mi_color = mensaje["color"]
            self.mi_id = mensaje["jugador_id"]
            print(f"\n🎨 Te asignaron el color: {self.mi_color.upper()}")
            print(f"👤 Tu ID: {self.mi_id}")
        
        elif tipo == proto.MSG_ESPERANDO:
            conectados = mensaje["conectados"]
            requeridos = mensaje["requeridos"]
            print(f"\n⏳ Esperando jugadores... ({conectados}/{requeridos})")
        
        elif tipo == proto.MSG_INICIO_JUEGO:
            self.juego_iniciado = True
            self.jugadores = mensaje["jugadores"]
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
            
            # ⭐ CLAVE: Resetear estado cuando ES mi turno (nuevo o mantenido)
            if self.es_mi_turno:
                # Si no era mi turno antes, o si era mi turno pero cambió algo, resetear
                if not era_mi_turno_anterior:
                    self.log_debug("🔄 Nuevo turno - reseteando estado de dados")
                    self.resetear_estado_dados()
                # Si ya era mi turno, verificar si debo resetear por mantener turno
                else:
                    # Solo resetear dados_lanzados si mantuvo turno por dobles
                    if self.ultimo_es_doble:
                        self.dados_lanzados = False
                        self.esperando_dados = False
                        self.esperando_movimiento = False
                        self.log_debug("🔄 Manteniendo turno por dobles - reseteando solo dados_lanzados")
                    else:
                        # Si no era doble y sigue siendo mi turno, algo raro pasó - resetear todo
                        self.resetear_estado_dados()
                        self.log_debug("🔄 Turno mantenido sin dobles - reseteando todo")
            else:
                # No es mi turno - resetear flags de espera
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
            
            # ⭐ Solo mostrar resultado si son MIS dados
            if self.es_mi_turno:
                dobles_msg = "¡DOBLES! 🎉" if self.ultimo_es_doble else ""
                print(f"\n🎲 RESULTADO: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma} {dobles_msg}")
                
                if self.ultimo_es_doble:
                    print("🔄 ¡Sacaste dobles! Puedes sacar una ficha de la cárcel y mantener tu turno.")
                else:
                    print("➡️ Sin dobles. Mueve una ficha y tu turno terminará.")
        
        elif tipo == proto.MSG_TABLERO:
            self.estado_tablero = mensaje
            self.log_debug("Estado del tablero actualizado")
        
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
            
            self.esperando_movimiento = False
        
        elif tipo == proto.MSG_ERROR:
            error_msg = mensaje['mensaje']
            print(f"\n❌ Error: {error_msg}")
            
            # Resetear flags de espera
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
            nombre = mensaje["nombre"]
            color = mensaje["color"]
            print(f"\n⚠️ {nombre} ({color}) se ha desconectado")
        
        elif tipo == proto.MSG_INFO:
            print(f"\nℹ️ {mensaje['mensaje']}")
    
    def enviar(self, mensaje):
        """Envía un mensaje al servidor"""
        try:
            data = json.dumps(mensaje, ensure_ascii=False).encode('utf-8')
            self.socket.send(data)
            self.log_debug(f"Mensaje enviado: {mensaje}")
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            self.conectado = False
    
    def esperar_respuesta_dados(self, timeout=5.0):
        """Espera específicamente la respuesta de dados"""
        tiempo_inicio = time.time()
        self.esperando_dados = True
        
        print("⏳ Esperando resultado de dados...")
        
        while self.esperando_dados and (time.time() - tiempo_inicio) < timeout:
            self.procesar_mensajes()
            time.sleep(0.1)
            
            # Mostrar puntos de progreso
            if int((time.time() - tiempo_inicio) * 10) % 10 == 0:
                print(".", end="", flush=True)
        
        if self.esperando_dados:
            print(f"\n⚠️ Timeout esperando dados ({timeout}s)")
            self.esperando_dados = False
            return False
        
        return True
    
    def esperar_respuesta_movimiento(self, timeout=3.0):
        """Espera respuesta de movimiento"""
        tiempo_inicio = time.time()
        self.esperando_movimiento = True
        
        while self.esperando_movimiento and (time.time() - tiempo_inicio) < timeout:
            self.procesar_mensajes()
            time.sleep(0.1)
        
        if self.esperando_movimiento:
            print(f"\n⚠️ Timeout esperando respuesta de movimiento")
            self.esperando_movimiento = False
            return False
        
        return True
    
    def mostrar_estado_dados(self):
        """⭐ CORREGIDO: Muestra el estado actual de los dados SOLO si son míos"""
        if self.dados_lanzados and self.es_mi_turno:
            dobles_info = " ¡DOBLES!" if self.ultimo_es_doble else ""
            print(f"🎲 Última tirada: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}{dobles_info}")
        else:
            print("🎲 No se han lanzado dados en este turno")
    
    def mostrar_mis_fichas(self):
        """Muestra las fichas del jugador actual con detalle completo"""
        if not self.estado_tablero or "jugadores" not in self.estado_tablero:
            print("⚠️ No hay información del tablero disponible")
            return
        
        # Buscar mis fichas
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
        fichas_en_meta = []
        
        for ficha in mi_info["fichas"]:
            if ficha["estado"] == "BLOQUEADO":
                fichas_bloqueadas.append(ficha)
            elif ficha["estado"] == "EN_JUEGO":
                fichas_en_juego.append(ficha)
            elif ficha["estado"] == "META":
                fichas_en_meta.append(ficha)
        
        # Mostrar fichas por categoría
        print("🔒 FICHAS EN CÁRCEL:")
        if fichas_bloqueadas:
            for ficha in fichas_bloqueadas:
                print(f"  └─ Ficha {ficha['id'] + 1}")
        else:
            print("  └─ Ninguna")
        
        print("\n🎮 FICHAS EN JUEGO:")
        if fichas_en_juego:
            for ficha in fichas_en_juego:
                # Calcular posición después del movimiento si se movieran
                futura_pos = ficha['posicion'] + self.ultima_suma if self.dados_lanzados and self.es_mi_turno else "?"
                movimiento_info = f" → C{futura_pos + 1}" if self.dados_lanzados and self.es_mi_turno and isinstance(futura_pos, int) else ""
                print(f"  └─ Ficha {ficha['id'] + 1}: C{ficha['posicion'] + 1}{movimiento_info}")
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
        
        # Información del turno
        if hasattr(self, 'jugadores') and self.jugadores:
            turno_actual = self.estado_tablero.get("turno_actual", 0)
            if turno_actual < len(self.jugadores):
                jugador_turno = self.jugadores[turno_actual]
                print(f"🎯 Turno actual: {jugador_turno['nombre']} ({jugador_turno['color'].upper()})")
        
        # Estado de dados (solo si es mi turno)
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
            
            # Mostrar posiciones de fichas en juego
            fichas_en_juego = [f for f in jugador["fichas"] if f["estado"] == "EN_JUEGO"]
            if fichas_en_juego:
                posiciones = [f"C{f['posicion'] + 1}" for f in fichas_en_juego]
                print(f"   📍 Posiciones: {', '.join(posiciones)}")
        
        print("="*60)
    
    def mostrar_tablero_visual(self):
        """Muestra el tablero de forma visual mejorada"""
        if not self.estado_tablero or "jugadores" not in self.estado_tablero:
            print("⚠️ No hay información del tablero disponible")
            return
        
        print("\n" + "="*80)
        print("🎲 TABLERO DE PARCHÍS 🎲".center(80))
        print("="*80)
        
        # Información de turno actual
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
        
        # Mostrar estado de dados (solo si es mi turno)
        if self.dados_lanzados and self.es_mi_turno:
            dados_info = f"🎲 Dados: [{self.ultimo_dado1}] [{self.ultimo_dado2}] = {self.ultima_suma}"
            if self.ultimo_es_doble:
                dados_info += " ¡DOBLES!"
            print(dados_info.center(80))
        
        print("="*80)
        
        # Crear mapa de posiciones con fichas
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
        
        # Mostrar tablero en filas
        total_casillas = 68
        casillas_por_fila = 8
        
        for fila in range(0, total_casillas, casillas_por_fila):
            print(f"\n📍 Casillas {fila + 1} a {min(fila + casillas_por_fila, total_casillas)}:")
            
            # Cabecera
            header = ""
            for i in range(fila, min(fila + casillas_por_fila, total_casillas)):
                header += f"{i+1:3d} "
            print(f"     {header}")
            
            # Contenido
            content = ""
            for i in range(fila, min(fila + casillas_por_fila, total_casillas)):
                fichas_aqui = posiciones_fichas.get(i, [])
                if fichas_aqui:
                    fichas_str = fichas_aqui[0][:3]  # Máximo 3 caracteres
                else:
                    fichas_str = "---"
                content += f"{fichas_str:>3s} "
            print(f"     {content}")
        
        # Leyenda y estadísticas
        print("\n" + "-"*80)
        print("LEYENDA: R=Rojo, A=Azul, Am=Amarillo, V=Verde (número = ID de ficha)")
        print("ESTADÍSTICAS:")
        
        for jugador in self.estado_tablero["jugadores"]:
            marca = "⭐" if jugador["color"] == self.mi_color else "  "
            print(f"{marca} {jugador['nombre']} ({jugador['color'].upper()}): "
                  f"🔒{jugador['bloqueadas']} | 🎮{jugador['en_juego']} | 🏁{jugador['en_meta']}")
        
        print("="*80)
    
    def menu_turno(self):
        """⭐ CORREGIDO: Muestra el menú principal durante el turno"""
        print(f"\n{'='*60}")
        print(f"🎯 TU TURNO - {self.mi_nombre} ({self.mi_color.upper()})".center(60))
        print(f"{'='*60}")
        
        # Mostrar estado actual
        self.mostrar_estado_dados()
        
        opciones = []
        
        # ⭐ CLAVE: Si no he lanzado dados EN ESTE TURNO, mostrar opción de lanzar
        if not self.dados_lanzados:
            opciones = [
                "🎲 Lanzar dados",
                "👀 Ver mis fichas", 
                "📊 Ver tablero completo",
                "🎯 Ver tablero visual",
                "🚪 Salir"
            ]
        else:
            # Ya se lanzaron los dados EN ESTE TURNO
            if self.ultimo_es_doble:
                opciones = [
                    "🔓 Sacar ficha de la cárcel",
                    "🎮 Mover ficha en juego",
                    "👀 Ver mis fichas",
                    "📊 Ver tablero completo", 
                    "🎯 Ver tablero visual",
                    "🚪 Salir"
                ]
            else:
                opciones = [
                    "🎮 Mover ficha en juego",
                    "👀 Ver mis fichas",
                    "📊 Ver tablero completo",
                    "🎯 Ver tablero visual", 
                    "🚪 Salir"
                ]
        
        print("\n¿Qué deseas hacer?")
        for i, opcion in enumerate(opciones, 1):
            print(f"{i}. {opcion}")
        
        try:
            opcion = input(f"\nOpción (1-{len(opciones)}): ").strip()
            return opcion, opciones
        except:
            return "0", opciones
    
    def ejecutar(self):
        """Loop principal del cliente mejorado"""
        print("\n" + "="*60)
        print("🎲 CLIENTE DE PARCHÍS 🎲".center(60))
        print("="*60)
        
        nombre = input("Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Jugador_{int(time.time()) % 1000}"
        
        if not self.conectar(nombre):
            return
        
        print("\n⏳ Esperando que el juego comience...")
        
        # Loop principal mejorado
        while self.running and self.conectado:
            # Procesar mensajes pendientes SIEMPRE
            self.procesar_mensajes()
            
            # Si no es mi turno o el juego no ha iniciado, esperar
            if not self.juego_iniciado or not self.es_mi_turno:
                time.sleep(0.2)
                continue
            
            # Es mi turno - mostrar menú
            opcion, opciones = self.menu_turno()
            
            # Procesar opción
            try:
                opcion_num = int(opcion)
                if opcion_num < 1 or opcion_num > len(opciones):
                    print("⚠️ Opción no válida")
                    continue
                
                accion = opciones[opcion_num - 1]
                
                if "Lanzar dados" in accion:
                    print("\n🎲 Lanzando dados...")
                    self.enviar(proto.mensaje_lanzar_dados())
                    
                    # Esperar resultado específicamente
                    if self.esperar_respuesta_dados():
                        print("✅ Dados recibidos correctamente")
                    else:
                        print("❌ Error recibiendo dados")
                
                elif "Sacar ficha" in accion:
                    print("\n🔓 Intentando sacar ficha de la cárcel...")
                    self.enviar(proto.mensaje_sacar_carcel())
                    self.esperar_respuesta_movimiento()
                
                elif "Mover ficha en juego" in accion:
                    self.elegir_y_mover_ficha()
                
                elif "Ver mis fichas" in accion:
                    self.mostrar_mis_fichas()
                    input("\nPresiona Enter para continuar...")
                
                elif "Ver tablero completo" in accion:
                    self.mostrar_tablero_completo()
                    input("\nPresiona Enter para continuar...")
                
                elif "Ver tablero visual" in accion:
                    self.mostrar_tablero_visual()
                    input("\nPresiona Enter para continuar...")
                
                elif "Salir" in accion:
                    print("\n👋 Saliendo del juego...")
                    break
                
            except ValueError:
                print("⚠️ Ingresa un número válido")
                continue
            except Exception as e:
                print(f"❌ Error procesando opción: {e}")
                continue
        
        self.desconectar()
    
    def elegir_y_mover_ficha(self):
        """Permite al jugador elegir qué ficha mover con información detallada"""
        print("\n" + "─"*50)
        print("🎮 MOVER FICHA".center(50))
        print("─"*50)
        
        self.mostrar_mis_fichas()
        
        try:
            ficha_num = int(input(f"\n¿Qué ficha deseas mover? (1-{proto.FICHAS_POR_JUGADOR}): "))
            if 1 <= ficha_num <= proto.FICHAS_POR_JUGADOR:
                print(f"\n🎮 Moviendo ficha {ficha_num}...")
                self.enviar(proto.mensaje_mover_ficha(ficha_num - 1))
                self.esperar_respuesta_movimiento()
            else:
                print(f"⚠️ Número de ficha inválido (debe ser 1-{proto.FICHAS_POR_JUGADOR})")
        except ValueError:
            print("⚠️ Ingresa un número válido")
    
    def desconectar(self):
        """Desconecta del servidor"""
        self.running = False
        self.conectado = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("\n👋 Desconectado del servidor")


if __name__ == "__main__":
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
        cliente.ejecutar()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupción recibida...")
        cliente.desconectar()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        cliente.desconectar()
