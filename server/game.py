
import random
import gameFile as tkn
from user import User
from parchis import Table

def lanzar_dados():
    """Lanza dos dados y retorna los valores"""
    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    return dado1, dado2

def es_par(dado1, dado2):
    """Verifica si los dos dados son iguales (par)"""
    return dado1 == dado2

COLORES = {
    1: "rojo",
    2: "azul",
    3: "amarillo",
    4: "verde"
}

def configurar_jugadores():
    """Configura los jugadores al inicio del juego"""
    jugadores = []
    num_jugadores = 0
    
    while num_jugadores < 2 or num_jugadores > 4:
        try:
            num_jugadores = int(input("¿Cuántos jugadores van a jugar? (2-4): "))
            if num_jugadores < 2 or num_jugadores > 4:
                print("⚠️ Debe ser entre 2 y 4 jugadores")
        except ValueError:
            print("⚠️ Por favor ingresa un número válido")
    
    colores_disponibles = list(COLORES.values())
    
    for i in range(num_jugadores):
        print(f"\n--- Configuración Jugador {i+1} ---")
        nombre = input(f"Ingresa el nombre del jugador {i+1}: ")
        
        print("\n🎨 Escoge un color:")
        for idx, color in enumerate(colores_disponibles, start=1):
            print(f"  {idx}. {color.capitalize()}")
        
        while True:
            try:
                opcion = int(input("Opción: "))
                if 1 <= opcion <= len(colores_disponibles):
                    color = colores_disponibles.pop(opcion - 1)
                    break
                else:
                    print("⚠️ Opción inválida. Intenta de nuevo.")
            except ValueError:
                print("⚠️ Por favor ingresa un número válido")
        
        usuario = User(nombre, color)
        
        # Agregar 4 fichas bloqueadas a cada jugador
        for _ in range(4):
            usuario.agregar_ficha(tkn.gameToken(color, "BLOQUEADO"))
        
        jugadores.append(usuario)
        print(f"✓ {nombre} jugará con el color {color}")
    
    return jugadores

def turno_jugador(jugador, tablero, indice_color):
    """Ejecuta el turno completo de un jugador"""
    print("\n" + "="*70)
    print(f"🎯 TURNO DE {jugador.name.upper()} ({jugador.color.upper()})".center(70))
    print("="*70)
    
    # Mostrar estado actual del jugador
    print(f"\n📊 Estado: {jugador}")
    
    input("\n⏎ Presiona ENTER para lanzar los dados...")
    
    # Lanzar dos dados
    dado1, dado2 = lanzar_dados()
    suma = dado1 + dado2
    es_doble = es_par(dado1, dado2)
    
    print(f"\n🎲 Dados: [{dado1}] [{dado2}] = {suma}")
    
    if es_doble:
        print(f"🎉 ¡DOBLES! Puedes sacar una ficha de la cárcel")
    
    # Verificar si puede sacar ficha de la cárcel
    if es_doble and jugador.fichas_bloqueadas() > 0:
        print("\n¿Quieres sacar una ficha de la cárcel?")
        print("1. Sí")
        print("2. No (usar el movimiento para fichas en juego)")
        
        try:
            opcion = int(input("Opción: "))
            if opcion == 1:
                salida = tablero.salidas[indice_color]
                if jugador.desbloquear_ficha(salida):
                    print(f"✓ Ficha liberada a la casilla {salida + 1}")
                    return True  # Turno exitoso
        except ValueError:
            print("⚠️ Opción inválida, se usará el movimiento normal")
    
    # Si hay fichas en juego, permitir moverlas
    fichas_juego = jugador.fichas_en_juego()
    
    if fichas_juego:
        print(f"\n📍 Tienes {len(fichas_juego)} ficha(s) en juego")
        jugador.mostrar_fichas()
        
        while True:
            try:
                eleccion = int(input(f"\n¿Qué ficha quieres mover? (1-{len(jugador.fichas)}): ")) - 1
                
                if 0 <= eleccion < len(jugador.fichas):
                    if jugador.fichas[eleccion].estado == "EN_JUEGO":
                        jugador.fichas[eleccion].mover(suma, tablero)
                        break
                    else:
                        print("⚠️ Esa ficha no está en juego")
                else:
                    print("⚠️ Número de ficha inválido")
            except ValueError:
                print("⚠️ Por favor ingresa un número válido")
    else:
        if not es_doble:
            print("\n❌ No tienes fichas en juego y no sacaste dobles")
            print("   Pierdes el turno")
        else:
            print("\n⚠️ No tienes fichas en juego para mover")
    
    return True

def main():
    print("\n" + "="*70)
    print("🎲 BIENVENIDO AL PARCHÍS 🎲".center(70))
    print("="*70 + "\n")
    
    tablero = Table()
    jugadores = configurar_jugadores()
    
    print("\n" + "="*70)
    print("🎮 JUGADORES LISTOS 🎮".center(70))
    print("="*70)
    for jugador in jugadores:
        print(f"  • {jugador}")
    
    print("\n¡Comienza el juego!\n")
    input("⏎ Presiona ENTER para comenzar...")
    
    turno = 0
    max_turnos = 1000  # Límite de seguridad
    
    while turno < max_turnos:
        jugador_actual = jugadores[turno % len(jugadores)]
        indice_color = [j.color for j in jugadores].index(jugador_actual.color)
        
        # Mostrar tablero cada ciertos turnos (opcional)
        if turno % (len(jugadores) * 3) == 0 and turno > 0:
            tablero.mostrar_tablero(jugadores)
            tablero.mostrar_resumen(jugadores)
        
        # Ejecutar turno
        turno_jugador(jugador_actual, tablero, indice_color)
        
        # Verificar si ganó
        if jugador_actual.ha_ganado():
            print("\n" + "🏆"*35)
            print(f"🎉 ¡¡¡{jugador_actual.name.upper()} HA GANADO!!! 🎉".center(70))
            print("🏆"*35 + "\n")
            tablero.mostrar_tablero(jugadores)
            break
        
        # Opción para ver el tablero
        if len(jugador_actual.fichas_en_juego()) > 0:
            ver = input("\n¿Ver tablero completo? (s/n): ").lower()
            if ver == 's':
                tablero.mostrar_tablero(jugadores)
                tablero.mostrar_resumen(jugadores)
        
        turno += 1
    
    if turno >= max_turnos:
        print("\n⚠️ Se alcanzó el límite de turnos. Juego terminado.")

if __name__ == "__main__":
    main()
