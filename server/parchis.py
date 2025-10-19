class Table:
    def __init__(self):
        self.boxes = [""] * 68  # Casillas normales
        # Casillas de salida por color
        self.salidas = {
            'rojo': 38,     # Casilla 39
            'verde': 55,    # Casilla 56
            'amarillo': 4,  # Casilla 5
            'azul': 21      # Casilla 22
        }
        
        # Casillas seguras antes de meta
        self.seguro_meta = {
            'rojo': 33,     # Casilla 34
            'verde': 50,    # Casilla 51
            'amarillo': 67, # Casilla 68
            'azul': 16      # Casilla 17
        }
        
        # Casillas seguras normales
        self.save = [12, 17, 29, 34, 46, 51, 63, 68]  
        
        # Casillas de meta para cada color (7 casillas + meta)
        self.casillas_meta = {
            'rojo': ['sr1','sr2','sr3','sr4','sr5','sr6','sr7','META'],
            'verde': ['sv1','sv2','sv3','sv4','sv5','sv6','sv7','META'],
            'amarillo': ['sa1','sa2','sa3','sa4','sa5','sa6','sa7','META'],
            'azul': ['sB1','sB2','sB3','sB4','sB5','sB6','sB7','META']
        }
        
        self._begin_table()

    def _begin_table(self):
        """Inicializa las casillas del tablero"""
        # Inicializar casillas normales
        for i in range(68):
            self.boxes[i] = f"C{i+1}"
        
        # Marcar casillas de salida
        for color, salida in self.salidas.items():
            self.boxes[salida] = f"SALIDA_{color.upper()}"
        
        # Marcar casillas seguras
        for save in self.save:
            self.boxes[save - 1] = "SEGURO"
            
        # Marcar casillas de entrada a meta
        for color, seguro in self.seguro_meta.items():
            self.boxes[seguro] = f"SEGURO_META_{color.upper()}"
    
    def mostrar_tablero(self, jugadores):
        """Muestra el tablero con las fichas de todos los jugadores"""
        print("\n" + "="*80)
        print("🎲 TABLERO DE PARCHÍS 🎲".center(80))
        print("="*80)
        
        # Crear un mapa de posiciones con fichas
        posiciones_fichas = {}
        posiciones_meta = {color: {} for color in self.casillas_meta.keys()}
        
        for jugador in jugadores:
            color = jugador.color
            for idx, ficha in enumerate(jugador.fichas):
                if ficha.estado == "EN_JUEGO":
                    if ficha.posicion >= 0:
                        if ficha.posicion not in posiciones_fichas:
                            posiciones_fichas[ficha.posicion] = []
                        posiciones_fichas[ficha.posicion].append(f"{color[0].upper()}{idx+1}")
                elif ficha.estado == "CAMINO_META":
                    pos_meta = ficha.posicion_meta
                    if pos_meta not in posiciones_meta[color]:
                        posiciones_meta[color][pos_meta] = []
                    posiciones_meta[color][pos_meta].append(f"{color[0].upper()}{idx+1}")
        
        # Mostrar tablero principal
        print("\n=== TABLERO PRINCIPAL ===")
        for inicio in range(0, 68, 10):
            fin = min(inicio + 10, 68)
            print(f"\n📍 Casillas {inicio + 1} a {fin}:")
            
            for i in range(inicio, fin):
                casilla = self.boxes[i]
                
                # Determinar símbolo según tipo de casilla
                if "SALIDA" in casilla:
                    simbolo = "🚪"
                elif "SEGURO_META" in casilla:
                    simbolo = "🎯"
                elif "SEGURO" in casilla:
                    simbolo = "🛡️"
                else:
                    simbolo = "⬜"
                
                # Mostrar fichas en esta casilla
                fichas = posiciones_fichas.get(i, [])
                fichas_str = ",".join(fichas) if fichas else "---"
                
                print(f"  [{i+1:2d}] {simbolo} {casilla:15s} | {fichas_str}")
        
        # Mostrar caminos a meta
        print("\n=== CAMINOS A META ===")
        for color in self.casillas_meta:
            print(f"\n🎯 Camino a meta {color.upper()}:")
            for idx, casilla in enumerate(self.casillas_meta[color]):
                fichas = posiciones_meta[color].get(idx, [])
                fichas_str = ",".join(fichas) if fichas else "---"
                print(f"  [{casilla:4s}] | {fichas_str}")
        
        # Leyenda
        print("\n" + "-"*80)
        print("LEYENDA: 🚪=Salida | 🎯=Entrada Meta | 🛡️=Seguro | ⬜=Normal")
        print("FICHAS: R=Rojo, A=Azul, Am=Amarillo, V=Verde (número = ID ficha)")
        print("="*80)
    
    def mostrar_resumen(self, jugadores):
        """Muestra un resumen rápido de todas las fichas"""
        print("\n📊 RESUMEN DE FICHAS:")
        print("-" * 60)
        for jugador in jugadores:
            bloqueadas = sum(1 for f in jugador.fichas if f.estado == "BLOQUEADO")
            en_juego = sum(1 for f in jugador.fichas if f.estado == "EN_JUEGO")
            en_meta = sum(1 for f in jugador.fichas if f.estado == "META")
            
            print(f"{jugador.name:12s} ({jugador.color:8s}): "
                  f"🔒{bloqueadas} | 🎮{en_juego} | 🏁{en_meta}")
        print("-" * 60 + "\n")
    
    def esta_cerca_meta(self, ficha):
        """
        Verifica si una ficha está a 7 o menos casillas de su entrada a meta
        """
        if ficha.estado != "EN_JUEGO":
            return False
            
        seguro_meta = self.seguro_meta[ficha.color]
        casillas_hasta_meta = 0
        
        # Si la ficha está antes del seguro_meta
        if ficha.posicion <= seguro_meta:
            casillas_hasta_meta = seguro_meta - ficha.posicion
        else:
            # Si la ficha está después, debe dar la vuelta
            casillas_hasta_meta = (68 - ficha.posicion) + seguro_meta
        
        return casillas_hasta_meta <= 7


if __name__ == "__main__":
    table1 = Table()
    print("Tablero de Parchís inicializado")
    print(f"Total de casillas: {len(table1.boxes)}")
    print(f"Salidas en: {[s+1 for s in table1.salidas]}")
    print(f"Seguros en: {table1.save}")
