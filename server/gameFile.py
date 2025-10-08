class gameToken:
    def __init__(self, color, estado):
        self.color = color
        self.estado = estado  # BLOQUEADO, EN_JUEGO, META
        self.posicion = -1  # -1 = en cárcel
    
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
        
        posicion_anterior = self.posicion
        nueva_posicion = self.posicion + pasos
        
        # Verificar si llega a la meta (simplificado, luego mejoramos)
        if nueva_posicion >= len(tablero.boxes):
            nueva_posicion = len(tablero.boxes) - 1
            self.estado = "META"
            print(f"🏁 ¡Ficha {self.color} llegó a la META!")
        
        self.posicion = nueva_posicion
        print(f"→ Ficha {self.color} se movió de C{posicion_anterior + 1} a C{self.posicion + 1}")
        return True
    
    def __str__(self):
        estado_emoji = {
            "BLOQUEADO": "🔒",
            "EN_JUEGO": "🎮",
            "META": "🏁"
        }
        return f"{estado_emoji.get(self.estado, '❓')} Ficha {self.color} - Pos: {self.posicion if self.posicion >= 0 else 'CÁRCEL'} - Estado: {self.estado}"
