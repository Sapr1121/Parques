MSG_CONECTAR = "CONECTAR"
MSG_LANZAR_DADOS = "LANZAR_DADOS"
MSG_SACAR_CARCEL = "SACAR_CARCEL"
MSG_MOVER_FICHA = "MOVER_FICHA"
MSG_DESCONECTAR = "DESCONECTAR"
MSG_LISTO = "LISTO" 





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

MAX_JUGADORES = 4
MIN_JUGADORES = 2
FICHAS_POR_JUGADOR = 4

COLORES = ["rojo", "azul", "amarillo", "verde"]

ESTADO_BLOQUEADO = "BLOQUEADO"
ESTADO_EN_JUEGO = "EN_JUEGO"
ESTADO_META = "META"


def crear_mensaje(tipo, **kwargs):
    """Crea un mensaje en formato diccionario"""
    mensaje = {"tipo": tipo}
    mensaje.update(kwargs)
    return mensaje

def mensaje_listo():
    return crear_mensaje(MSG_LISTO)

def mensaje_conectar(nombre):
    return crear_mensaje(MSG_CONECTAR, nombre=nombre)

def mensaje_lanzar_dados():
    return crear_mensaje(MSG_LANZAR_DADOS)

def mensaje_sacar_carcel():
    return crear_mensaje(MSG_SACAR_CARCEL)

def mensaje_mover_ficha(ficha_id):
    return crear_mensaje(MSG_MOVER_FICHA, ficha_id=ficha_id)

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

def mensaje_info(mensaje, es_admin=None):
    msg = crear_mensaje(MSG_INFO, mensaje=mensaje)
    if es_admin is not None:
        msg["es_admin"] = bool(es_admin)
    return msg

