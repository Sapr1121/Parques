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