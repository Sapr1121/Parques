# ============================================
# TIPOS DE MENSAJES: CLIENTE → SERVIDOR
# ============================================
MSG_CONECTAR = "CONECTAR"
MSG_LANZAR_DADOS = "LANZAR_DADOS"
MSG_SACAR_CARCEL = "SACAR_CARCEL"
MSG_MOVER_FICHA = "MOVER_FICHA"
MSG_DESCONECTAR = "DESCONECTAR"
MSG_LISTO = "LISTO"  # Cliente listo para empezar
MSG_SACAR_TODAS = "SACAR_TODAS"  # Solicitar sacar todas las fichas de la cárcel   
MSG_SOLICITAR_COLORES = "SOLICITAR_COLORES" 
MSG_DEBUG_FORZAR_TRES_DOBLES = "DEBUG_FORZAR_TRES_DOBLES"  # ⭐ NUEVO
MSG_ELEGIR_FICHA_PREMIO = "ELEGIR_FICHA_PREMIO"  # ⭐ NUEVO


# ============================================
# TIPOS DE MENSAJES: SERVIDOR → CLIENTE
# ============================================
MSG_BIENVENIDA = "BIENVENIDA"
MSG_ESPERANDO = "ESPERANDO"
MSG_INICIO_JUEGO = "INICIO_JUEGO"
MSG_TURNO = "TURNO"
MSG_DADOS = "DADOS"
MSG_TABLERO = "TABLERO"
MSG_MOVIMIENTO_OK = "MOVIMIENTO_OK"
MSG_ERROR = "ERROR"
MSG_VICTORIA = "VICTORIA"
MSG_JUGADOR_DESCONECTADO = "JUGADOR_DESCONECTADO"
MSG_CAPTURA = "CAPTURA"
MSG_INFO = "INFO"  # Mensajes informativos generales
MSG_COLORES_DISPONIBLES = "COLORES_DISPONIBLES"

# Mensajes para determinación de turnos
MSG_DETERMINACION_INICIO = "DETERMINACION_INICIO"  # Servidor inicia fase de determinación
MSG_DETERMINACION_TIRADA = "DETERMINACION_TIRADA"  # Cliente envía su tirada
MSG_DETERMINACION_RESULTADO = "DETERMINACION_RESULTADO"  # Servidor envía resultado de tirada
MSG_DETERMINACION_EMPATE = "DETERMINACION_EMPATE"  # Servidor notifica empate
MSG_DETERMINACION_GANADOR = "DETERMINACION_GANADOR"  # Servidor anuncia ganador y orden


# ============================================
# CONFIGURACIÓN DEL JUEGO
# ============================================
MAX_JUGADORES = 4
MIN_JUGADORES = 2
FICHAS_POR_JUGADOR = 4

# ============================================
# COLORES DISPONIBLES
# ============================================
COLORES = ["rojo", "azul", "amarillo", "verde"]

# ============================================
# ESTADOS DE FICHA
# ============================================
ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_EN_JUEGO = "EN_JUEGO"
ESTADO_META = "META"

# ============================================
# FUNCIONES HELPER PARA MENSAJES
# ============================================

def crear_mensaje(tipo, **kwargs):
    """Crea un mensaje en formato diccionario"""
    mensaje = {"tipo": tipo}
    mensaje.update(kwargs)
    return mensaje

def mensaje_listo():
    return crear_mensaje(MSG_LISTO)

def mensaje_conectar(nombre, color=None):  
    msg = crear_mensaje(MSG_CONECTAR, nombre=nombre)
    if color:
        msg["color"] = color
    return msg

def mensaje_solicitar_colores():
    """Solicita la lista de colores disponibles"""
    return crear_mensaje(MSG_SOLICITAR_COLORES)


def mensaje_colores_disponibles(colores):
    """Crea mensaje con colores disponibles"""
    return crear_mensaje(MSG_COLORES_DISPONIBLES, colores=colores)

def mensaje_lanzar_dados():
    return crear_mensaje(MSG_LANZAR_DADOS)

def mensaje_sacar_carcel():
    return crear_mensaje(MSG_SACAR_CARCEL)

def mensaje_mover_ficha(ficha_id, dado_elegido):
    """
    Crea un mensaje para mover una ficha.
    dado_elegido: 1 = primer dado, 2 = segundo dado, 3 = suma de dados
    """
    return crear_mensaje(MSG_MOVER_FICHA, ficha_id=ficha_id, dado_elegido=dado_elegido)

def mensaje_bienvenida(color, jugador_id, nombre):
    return crear_mensaje(MSG_BIENVENIDA, color=color, jugador_id=jugador_id, nombre=nombre)

def mensaje_esperando(conectados, requeridos):
    return crear_mensaje(MSG_ESPERANDO, conectados=conectados, requeridos=requeridos)

def mensaje_turno(nombre, color):
    return crear_mensaje(MSG_TURNO, nombre=nombre, color=color)

def mensaje_dados(dado1, dado2, suma, es_doble):
    return crear_mensaje(MSG_DADOS, dado1=dado1, dado2=dado2, suma=suma, es_doble=es_doble)

def mensaje_error(mensaje):
    return crear_mensaje(MSG_ERROR, mensaje=mensaje)

def mensaje_victoria(ganador, color):
    return crear_mensaje(MSG_VICTORIA, ganador=ganador, color=color)

def mensaje_info(mensaje, es_admin=None, es_host=None):
    """
    Crea un mensaje informativo general.
    
    Args:
        mensaje: Texto del mensaje
        es_admin: (opcional) Si es para el admin
        es_host: (opcional) Si es para el host
    """
    msg = crear_mensaje(MSG_INFO, mensaje=mensaje)
    if es_admin is not None:
        msg["es_admin"] = bool(es_admin)
    if es_host is not None:
        msg["es_host"] = bool(es_host)
    return msg

def mensaje_sacar_todas():
    return crear_mensaje(MSG_SACAR_TODAS)


# ============================================
# Sincronizacion PING/PONG
# ============================================
MSG_SYNC_REQUEST = "SYNC_REQUEST"
MSG_SYNC_RESPONSE = "SYNC_RESPONSE"

def mensaje_sync_request(t1):
    return crear_mensaje(MSG_SYNC_REQUEST, t1=t1)

def mensaje_sync_response(t1, t2, t3):
    return crear_mensaje(MSG_SYNC_RESPONSE, t1=t1, t2=t2, t3=t3)

# ============================================
# Mensajes para Determinación de Turnos
# ============================================

def mensaje_determinacion_inicio(jugador_actual=""):
    """Servidor inicia la fase de determinación de turnos"""
    return crear_mensaje(MSG_DETERMINACION_INICIO, 
                        mensaje="Todos los jugadores deben lanzar los dados una vez para determinar el orden",
                        jugador_actual=jugador_actual)

def mensaje_determinacion_tirada(dado1, dado2):
    """Cliente envía su tirada durante la determinación"""
    return crear_mensaje(MSG_DETERMINACION_TIRADA, dado1=dado1, dado2=dado2)

def mensaje_determinacion_resultado(nombre, color, dado1, dado2, suma, siguiente=""):
    """Servidor notifica el resultado de una tirada durante determinación"""
    return crear_mensaje(MSG_DETERMINACION_RESULTADO,
                        nombre=nombre,
                        color=color,
                        dado1=dado1,
                        dado2=dado2,
                        suma=suma,
                        siguiente=siguiente)

def mensaje_determinacion_empate(jugadores_empatados, valor_empate):
    """Servidor notifica que hay un empate y quiénes deben volver a tirar"""
    return crear_mensaje(MSG_DETERMINACION_EMPATE,
                        jugadores=jugadores_empatados,
                        valor=valor_empate,
                        mensaje=f"Empate con {valor_empate} puntos. Los jugadores empatados deben volver a tirar.")

def mensaje_determinacion_ganador(ganador_nombre, ganador_color, orden_turnos):
    """Servidor anuncia el ganador y el orden final de turnos"""
    return crear_mensaje(MSG_DETERMINACION_GANADOR,
                        ganador={"nombre": ganador_nombre, "color": ganador_color},
                        orden=orden_turnos,
                        mensaje=f"{ganador_nombre} ({ganador_color}) obtuvo el puntaje más alto y comenzará primero")

# ⭐ NUEVO: Mensajes para premio de 3 dobles
MSG_PREMIO_TRES_DOBLES = "PREMIO_TRES_DOBLES"
MSG_ELEGIR_FICHA_PREMIO = "ELEGIR_FICHA_PREMIO"
MSG_FICHA_A_META = "FICHA_A_META"

def mensaje_premio_tres_dobles(nombre, fichas_elegibles):
    """Notifica que el jugador ganó el premio de 3 dobles"""
    return {
        "tipo": MSG_PREMIO_TRES_DOBLES,
        "nombre": nombre,
        "fichas_elegibles": fichas_elegibles,
        "mensaje": f"{nombre} sacó 3 dobles consecutivos y puede enviar UNA ficha a META"
    }

def mensaje_elegir_ficha_premio(ficha_id):
    """Cliente envía la ficha elegida para enviar a META"""
    return {
        "tipo": MSG_ELEGIR_FICHA_PREMIO,
        "ficha_id": ficha_id
    }

def mensaje_ficha_a_meta(nombre, color, ficha_id, desde, estado_anterior):
    """Notifica que una ficha fue enviada a META por premio"""
    return {
        "tipo": MSG_FICHA_A_META,
        "nombre": nombre,
        "color": color,
        "ficha_id": ficha_id,
        "desde": desde,
        "estado_anterior": estado_anterior
    }

def mensaje_debug_forzar_tres_dobles():
    return {"tipo": MSG_DEBUG_FORZAR_TRES_DOBLES}