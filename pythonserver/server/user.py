import gameFile

class User:
    def __init__(self, name, color):
        self.name = name
        self.color = color 
        self.fichas = []
    
    def agregar_ficha(self, ficha):
        """Agrega una ficha al jugador (máximo 4)"""
        if len(self.fichas) < 4:
            self.fichas.append(ficha)
        else:
            print("✗ Ya tienes 4 fichas asignadas")
    
    def mostrar_fichas(self):
        """Muestra todas las fichas del jugador"""
        print(f"\n🎮 Fichas de {self.name} ({self.color}):")
        print("-" * 50)
        for i, ficha in enumerate(self.fichas):
            print(f"  {i+1}. {ficha}")
        print("-" * 50)
    
    def desbloquear_ficha(self, salida):
        """Desbloquea una ficha y la coloca en la salida"""
        for ficha in self.fichas:
            if ficha.estado == "BLOQUEADO":
                ficha.desbloquear(salida)
                return True
        print("✗ No hay fichas bloqueadas para desbloquear")
        return False
    
    def fichas_en_juego(self):
        """Retorna lista de fichas que están en el tablero"""
        return [f for f in self.fichas if f.estado == "EN_JUEGO"]
    
    def fichas_bloqueadas(self):
        """Retorna cantidad de fichas en cárcel"""
        return sum(1 for f in self.fichas if f.estado == "BLOQUEADO")
    
    def fichas_en_meta(self):
        """Retorna cantidad de fichas que llegaron a la meta"""
        return sum(1 for f in self.fichas if f.estado == "META")
    
    def ha_ganado(self):
        """Verifica si el jugador ganó (todas las fichas en meta)"""
        return self.fichas_en_meta() == 4
    
    def __str__(self):
        return f"{self.name} ({self.color}): {self.fichas_bloqueadas()}🔒 {len(self.fichas_en_juego())}🎮 {self.fichas_en_meta()}🏁"
