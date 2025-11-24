class gameToken:
    def __init__(self, color, estado):
        self.color = color
        self.estado = estado  # BLOQUEADO, EN_JUEGO, CAMINO_META, META
        self.posicion = -1    # -1 = en cárcel, 0-67 = en tablero
        self.posicion_meta = -1  # -1 = no en meta, 0-7 = camino a meta
    
    def desbloquear(self, salida):
        """Saca la ficha de la cárcel a la casilla de salida"""
        self.estado = "EN_JUEGO"
        self.posicion = salida
        print(f"✓ Ficha {self.color} desbloqueada en casilla {salida + 1}")
    
    def mover(self, pasos, tablero):
        """Mueve la ficha en el tablero"""
        if self.estado == "BLOQUEADO":
            print("✗ La ficha está bloqueada en la cárcel")
            return False
        
        if self.estado == "META":
            print("✗ La ficha ya está en meta")
            return False
            
        if self.estado == "CAMINO_META":
            # Mover en el camino a meta
            nueva_posicion_meta = self.posicion_meta + pasos
            if nueva_posicion_meta == 7:  # Llegó a META
                self.estado = "META"
                self.posicion_meta = 7
                print(f"🏁 ¡Ficha {self.color} llegó a la META!")
                return True
            elif nueva_posicion_meta < 7:  # Avanza en camino a meta
                self.posicion_meta = nueva_posicion_meta
                print(f"→ Ficha {self.color} avanzó a {tablero.casillas_meta[self.color][nueva_posicion_meta]}")
                return True
            return False  # No puede pasar de la meta
        
        # Mover en el tablero principal
        posicion_anterior = self.posicion
        nueva_posicion = self.posicion + pasos
        
        # Si pasa de 68, volver a empezar
        if nueva_posicion >= 68:
            nueva_posicion = nueva_posicion - 68
        
        # Verificar si llega o pasa por su seguro de meta
        if self.posicion <= tablero.seguro_meta[self.color] and nueva_posicion > tablero.seguro_meta[self.color]:
            pasos_restantes = nueva_posicion - tablero.seguro_meta[self.color]
            if pasos_restantes <= 7:  # Puede entrar al camino a meta
                self.estado = "CAMINO_META"
                self.posicion_meta = pasos_restantes - 1
                print(f"🎯 Ficha {self.color} entró al camino a meta en {tablero.casillas_meta[self.color][self.posicion_meta]}")
                return True
            
        self.posicion = nueva_posicion
        print(f"→ Ficha {self.color} se movió de C{posicion_anterior + 1} a C{self.posicion + 1}")
        return True
    
    def __str__(self):
        estado_emoji = {
            "BLOQUEADO": "🔒",
            "EN_JUEGO": "🎮",
            "META": "🏁",
            "CAMINO_META": "🛤️"
        }
        return f"{estado_emoji.get(self.estado, '❓')} Ficha {self.color} - Pos: {self.posicion if self.posicion >= 0 else 'CÁRCEL'} - Estado: {self.estado}"
