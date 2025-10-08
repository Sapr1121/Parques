class Table:
    def __init__(self):
        self.boxes = [""] * 68
        self.salidas = [5, 22, 39, 56]  # Casillas de salida por color (índices)
        self.save = [12, 17, 29, 34, 46, 51, 63, 68]  # Casillas seguras
        self.entradas = {
            'rojo': 4,      # Entrada a pasillo final
            'azul': 21,
            'amarillo': 38,
            'verde': 55
        }
        self._begin_table()
        
    def _begin_table(self):
        """Inicializa las casillas del tablero"""
        for i in range(68):
            self.boxes[i] = f"C{i+1}"
        
        for idx, salida in enumerate(self.salidas):
            self.boxes[salida] = "SALIDA"
        
        for save in self.save:
            self.boxes[save - 1] = "SEGURO"
    
    def mostrar_tablero(self, jugadores):
        """Muestra el tablero con las fichas de todos los jugadores"""
        print("\n" + "="*80)
        print("🎲 TABLERO DE PARCHÍS 🎲".center(80))
        print("="*80)
        
        # Crear un mapa de posiciones con fichas
        posiciones_fichas = {}
        for jugador in jugadores:
            for idx, ficha in enumerate(jugador.fichas):
                if ficha.posicion >= 0:  # Solo fichas en juego
                    pos = ficha.posicion
                    if pos not in posiciones_fichas:
                        posiciones_fichas[pos] = []
                    posiciones_fichas[pos].append(f"{ficha.color[0].upper()}{idx+1}")
        
        # Mostrar tablero en bloques de 10 casillas
        for inicio in range(0, 68, 10):
            fin = min(inicio + 10, 68)
            print(f"\n📍 Casillas {inicio + 1} a {fin}:")
            
            for i in range(inicio, fin):
                tipo_casilla = self.boxes[i]
                
                # Símbolo según tipo de casilla
                if "SALIDA" in tipo_casilla:
                    simbolo = "🚪"
                elif "SEGURO" in tipo_casilla:
                    simbolo = "🛡️"
                else:
                    simbolo = "⬜"
                
                # Mostrar fichas en esta casilla
                fichas_aqui = posiciones_fichas.get(i, [])
                fichas_str = ",".join(fichas_aqui) if fichas_aqui else "---"
                
                print(f"  [{i+1:2d}] {simbolo} {tipo_casilla:8s} | {fichas_str}")
        
        # Mostrar leyenda
        print("\n" + "-"*80)
        print("LEYENDA: 🚪=Salida | 🛡️=Seguro | ⬜=Normal")
        print("FICHAS: R=Rojo, A=Azul, Am=Amarillo, V=Verde (número = ficha)")
        print("="*80 + "\n")
    
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


if __name__ == "__main__":
    table1 = Table()
    print("Tablero de Parchís inicializado")
    print(f"Total de casillas: {len(table1.boxes)}")
    print(f"Salidas en: {[s+1 for s in table1.salidas]}")
    print(f"Seguros en: {table1.save}")
