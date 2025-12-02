"""
Sistema de base de datos para usuarios y estadísticas del juego Parchís
"""
import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), 'parques.db')

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        if self.conn is None:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP
            )
        ''')
        
        # Tabla de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resultado TEXT NOT NULL,
                color_jugado TEXT NOT NULL,
                fichas_en_meta INTEGER DEFAULT 0,
                turnos_jugados INTEGER DEFAULT 0,
                tiempo_juego INTEGER DEFAULT 0,
                jugadores_totales INTEGER DEFAULT 2,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabla de estadísticas globales por usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estadisticas (
                usuario_id INTEGER PRIMARY KEY,
                partidas_jugadas INTEGER DEFAULT 0,
                partidas_ganadas INTEGER DEFAULT 0,
                partidas_perdidas INTEGER DEFAULT 0,
                fichas_totales_en_meta INTEGER DEFAULT 0,
                tiempo_total_jugado INTEGER DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        print("✅ Base de datos inicializada correctamente")
    
    def hash_password(self, password: str) -> str:
        """Hashea una contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def registrar_usuario(self, username: str, password: str, email: Optional[str] = None) -> tuple:
        """Registra un nuevo usuario. Retorna (exito: bool, mensaje: str)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            if cursor.fetchone():
                return (False, 'El usuario ya existe')
            
            # Insertar nuevo usuario
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            usuario_id = cursor.lastrowid
            
            # Crear estadísticas iniciales
            cursor.execute('''
                INSERT INTO estadisticas (usuario_id)
                VALUES (?)
            ''', (usuario_id,))
            
            conn.commit()
            
            return (True, 'Usuario registrado exitosamente')
        except Exception as e:
            return (False, f'Error al registrar: {str(e)}')
    
    def autenticar_usuario(self, username: str, password: str) -> tuple:
        """Autentica un usuario. Retorna (exito: bool, mensaje: str, usuario_id: int|None)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, username, email, fecha_registro
                FROM usuarios
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            usuario = cursor.fetchone()
            
            if usuario:
                # Actualizar último acceso
                cursor.execute('''
                    UPDATE usuarios
                    SET ultimo_acceso = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (usuario['id'],))
                conn.commit()
                
                return (True, 'Login exitoso', usuario['id'])
            else:
                return (False, 'Usuario o contraseña incorrectos', None)
        except Exception as e:
            return (False, f'Error de autenticación: {str(e)}', None)
    
    def registrar_partida(self, usuario_id: int, resultado: str, color: str, 
                         fichas_meta: int = 0, turnos: int = 0, 
                         tiempo: int = 0, jugadores: int = 2) -> bool:
        """Registra una partida jugada"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insertar partida
            cursor.execute('''
                INSERT INTO partidas (usuario_id, resultado, color_jugado, 
                                     fichas_en_meta, turnos_jugados, tiempo_juego, jugadores_totales)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (usuario_id, resultado, color, fichas_meta, turnos, tiempo, jugadores))
            
            # Actualizar estadísticas
            cursor.execute('''
                UPDATE estadisticas
                SET partidas_jugadas = partidas_jugadas + 1,
                    partidas_ganadas = partidas_ganadas + ?,
                    partidas_perdidas = partidas_perdidas + ?,
                    fichas_totales_en_meta = fichas_totales_en_meta + ?,
                    tiempo_total_jugado = tiempo_total_jugado + ?
                WHERE usuario_id = ?
            ''', (
                1 if resultado == 'VICTORIA' else 0,
                1 if resultado == 'DERROTA' else 0,
                fichas_meta,
                tiempo,
                usuario_id
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error al registrar partida: {e}")
            return False
    
    def obtener_estadisticas(self, usuario_id: int) -> Dict[str, Any]:
        """Obtiene las estadísticas de un usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Estadísticas globales
            cursor.execute('''
                SELECT * FROM estadisticas WHERE usuario_id = ?
            ''', (usuario_id,))
            stats = cursor.fetchone()
            
            if not stats:
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            # Últimas 10 partidas
            cursor.execute('''
                SELECT fecha, resultado, color_jugado, fichas_en_meta, turnos_jugados
                FROM partidas
                WHERE usuario_id = ?
                ORDER BY fecha DESC
                LIMIT 10
            ''', (usuario_id,))
            ultimas_partidas = [dict(row) for row in cursor.fetchall()]
            
            # Calcular tasa de victoria
            tasa_victoria = 0
            if stats['partidas_jugadas'] > 0:
                tasa_victoria = (stats['partidas_ganadas'] / stats['partidas_jugadas']) * 100
            
            return {
                'success': True,
                'partidas_jugadas': stats['partidas_jugadas'],
                'partidas_ganadas': stats['partidas_ganadas'],
                'partidas_perdidas': stats['partidas_perdidas'],
                'tasa_victoria': round(tasa_victoria, 2),
                'fichas_totales_en_meta': stats['fichas_totales_en_meta'],
                'tiempo_total_jugado': stats['tiempo_total_jugado'],
                'ultimas_partidas': ultimas_partidas
            }
        except Exception as e:
            return {'success': False, 'message': f'Error al obtener estadísticas: {str(e)}'}
    
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene información de un usuario por ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, fecha_registro
                FROM usuarios
                WHERE id = ?
            ''', (usuario_id,))
            
            usuario = cursor.fetchone()
            return dict(usuario) if usuario else None
        except Exception as e:
            print(f"❌ Error al obtener usuario: {e}")
            return None
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            self.conn = None

# Instancia global
db_manager = DatabaseManager()
