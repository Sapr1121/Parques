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
            # Mover en el camino a meta (debe entrar exactamente)
            nueva_posicion_meta = self.posicion_meta + pasos
            
            # Verificar límites del camino a meta (0-7, donde 7 = META)
            if nueva_posicion_meta > 7:
                # No puede pasar de META
                print(f"✗ Ficha {self.color} no puede avanzar: necesita exactamente {7 - self.posicion_meta} pasos (intentó {pasos})")
                return False
            elif nueva_posicion_meta == 7:
                # Llegó exactamente a META
                self.estado = "META"
                self.posicion_meta = 7
                self.posicion = -1  # Ya no está en el tablero
                print(f"🏁 ¡Ficha {self.color} llegó a la META!")
                return True
            else:
                # Avanza en el camino a meta (0-6)
                self.posicion_meta = nueva_posicion_meta
                casilla_nombre = tablero.casillas_meta[self.color][nueva_posicion_meta]
                print(f"→ Ficha {self.color} avanzó a {casilla_nombre} (posición {nueva_posicion_meta}/7)")
                return True
        
        # Mover en el tablero principal
        posicion_anterior = self.posicion
        seguro_meta_color = tablero.seguro_meta[self.color]
        
        # ⭐ CASO ESPECIAL: Si YA está en el seguro_meta, entrar directamente al camino
        if self.posicion == seguro_meta_color:
            # Ya está en la entrada, todos los pasos van al camino a meta
            if pasos <= 8:  # Puede entrar (máximo 8 pasos: sr1...sr7...META)
                if pasos == 8:
                    # Llegó exactamente a META
                    self.estado = "META"
                    self.posicion_meta = 7
                    self.posicion = -1
                    print(f"🏁 ¡Ficha {self.color} llegó a la META desde seguro_meta!")
                    return True
                else:
                    # Entra al camino a meta (pasos 1-7 = sr1 a sr7)
                    self.estado = "CAMINO_META"
                    self.posicion_meta = pasos - 1  # pasos=1 → sr1 (pos 0), pasos=2 → sr2 (pos 1)...
                    self.posicion = -1  # ⭐ CRÍTICO: Ya no está en el tablero principal
                    casilla_meta_nombre = tablero.casillas_meta[self.color][self.posicion_meta]
                    print(f"🎯 Ficha {self.color} entró al camino a meta en {casilla_meta_nombre} (posición {self.posicion_meta}/7)")
                    return True
            else:
                # Más de 8 pasos, no puede entrar
                print(f"✗ No puede entrar a meta desde seguro_meta: necesita máximo 8 pasos (intentó {pasos})")
                return False
        
        # ⭐ Verificar si PASA POR el seguro_meta durante este movimiento
        pasos_dados = 0
        posicion_temporal = self.posicion
        cruzo_meta = False
        pasos_antes_meta = 0
        
        # Simular el movimiento paso por paso
        while pasos_dados < pasos:
            pasos_dados += 1
            posicion_temporal += 1
            
            # Dar la vuelta al tablero si es necesario
            if posicion_temporal >= 68:
                posicion_temporal = 0
            
            # ¿Llegó exactamente al seguro_meta?
            if posicion_temporal == seguro_meta_color:
                cruzo_meta = True
                pasos_antes_meta = pasos_dados
                break
        
        # Si cruzó el seguro_meta viniendo de otra casilla
        if cruzo_meta:
            # Calcular pasos restantes DESPUÉS de llegar al seguro_meta
            # Ejemplo: pos=30, pasos=5, pasos_antes_meta=3
            # → pasos_restantes = 5 - 3 = 2 → sr1 (paso 1), sr2 (paso 2) → posicion_meta = 1
            pasos_restantes = pasos - pasos_antes_meta  # Pasos después de llegar a seguro_meta
            
            if pasos_restantes <= 8:  # Puede entrar al camino a meta
                if pasos_restantes == 8:
                    # Llegó exactamente a META
                    self.estado = "META"
                    self.posicion_meta = 7
                    self.posicion = -1
                    print(f"🏁 ¡Ficha {self.color} llegó a la META!")
                    return True
                else:
                    # Entra al camino a meta
                    self.estado = "CAMINO_META"
                    self.posicion_meta = pasos_restantes - 1
                    self.posicion = -1  # ⭐ CRÍTICO: Ya no está en el tablero principal
                    casilla_meta_nombre = tablero.casillas_meta[self.color][self.posicion_meta]
                    print(f"🎯 Ficha {self.color} entró al camino a meta en {casilla_meta_nombre} (posición {self.posicion_meta}/7)")
                    return True
            else:
                # Los pasos exceden el camino a meta, no puede entrar
                print(f"✗ No puede entrar a meta: pasos restantes ({pasos_restantes}) > 8")
                return False
        
        # No cruzó meta, mover normalmente en el tablero
        nueva_posicion = self.posicion + pasos
        if nueva_posicion >= 68:
            nueva_posicion = nueva_posicion - 68
        
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
