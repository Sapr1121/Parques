#!/usr/bin/env python3
"""
Hybrid.py - Sistema de Lobby con Códigos Hexadecimales
Integración completa con ParchisServer y ParchisClient
"""

import asyncio
import socket
import secrets
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import os

# Importar módulos de servidor y cliente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'client'))

from server import ParchisServer            
from client import ParchisClient


# ============================================================================
# SERVIDOR DE REGISTRO CENTRAL
# ============================================================================

class RegistryServer:
    """Servidor central que registra lobbies activos"""
    
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.lobbies = {}
        self.server = None
        
    async def handle_client(self, reader, writer):
        """Maneja peticiones de clientes"""
        addr = writer.get_extra_info('peername')
        print(f"📡 Registro: Conexión desde {addr}")
        
        try:
            data = await reader.read(1024)
            message = json.loads(data.decode())
            
            action = message.get("action")
            
            if action == "REGISTER":
                response = await self.register_lobby(message, addr)
            elif action == "QUERY":
                response = await self.query_lobby(message)
            elif action == "UNREGISTER":
                response = await self.unregister_lobby(message)
            elif action == "PING":
                response = {"status": "success", "message": "pong"}
            else:
                response = {"status": "error", "message": "Acción desconocida"}
            
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
        except Exception as e:
            print(f"❌ Registro: Error manejando cliente: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def register_lobby(self, message, addr):
        """Registra un nuevo lobby"""
        hex_code = message.get("hex_code")
        game_port = message.get("game_port")
        host_name = message.get("host_name", "Anónimo")
        ip_address = message.get("ip_address") or addr[0]
        
        if not hex_code or not game_port:
            return {"status": "error", "message": "Faltan parámetros"}
        
        self.clean_old_lobbies()
        
        self.lobbies[hex_code] = {
            "ip": ip_address,
            "port": game_port,
            "host_name": host_name,
            "created": datetime.now()
        }
        
        print(f"✅ Registro: Lobby {hex_code} -> {ip_address}:{game_port} ({host_name})")
        
        return {
            "status": "success",
            "message": "Lobby registrado",
            "hex_code": hex_code
        }
    
    async def query_lobby(self, message):
        """Consulta información de un lobby"""
        hex_code = message.get("hex_code", "").upper()
        
        if hex_code in self.lobbies:
            lobby_info = self.lobbies[hex_code]
            return {
                "status": "success",
                "lobby": {
                    "ip": lobby_info["ip"],
                    "port": lobby_info["port"],
                    "host_name": lobby_info["host_name"]
                }
            }
        else:
            return {
                "status": "error",
                "message": "Lobby no encontrado. Verifica el código."
            }
    
    async def unregister_lobby(self, message):
        """Elimina un lobby del registro"""
        hex_code = message.get("hex_code", "").upper()
        
        if hex_code in self.lobbies:
            del self.lobbies[hex_code]
            print(f"🗑️ Registro: Lobby {hex_code} eliminado")
            return {"status": "success", "message": "Lobby eliminado"}
        
        return {"status": "error", "message": "Lobby no encontrado"}
    
    def clean_old_lobbies(self):
        """Elimina lobbies con más de 1 hora"""
        now = datetime.now()
        expired = [
            code for code, info in self.lobbies.items()
            if now - info["created"] > timedelta(hours=1)
        ]
        
        for code in expired:
            del self.lobbies[code]
            print(f"🧹 Registro: Lobby expirado {code} eliminado")
    
    async def start(self):
        """Inicia el servidor de registro"""
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        
        addr = self.server.sockets[0].getsockname()
        print(f"\n{'='*70}")
        print(f"🌐 SERVIDOR DE REGISTRO ACTIVO".center(70))
        print(f"{'='*70}")
        print(f"📍 Escuchando en {addr[0]}:{addr[1]}")
        print(f"{'='*70}\n")
        
        async with self.server:
            await self.server.serve_forever()


# ============================================================================
# LOBBY MANAGER CON CÓDIGOS HEXADECIMALES
# ============================================================================

class LobbyManager:
    """Gestor de lobby que puede crear o unirse a partidas con códigos hex"""
    
    def __init__(self, registry_host="localhost", registry_port=9000):
        self.servidor = None
        self.cliente = None
        self.es_host = False
        self.hex_code = None
        self.puerto_default = 8001
        self.registry_host = registry_host
        self.registry_port = registry_port
        self.registry_process = None
        self.server_auto_started = False
    
    def generar_codigo_hex(self, length=8):
        """Genera código hexadecimal único"""
        return secrets.token_hex(length // 2).upper()
    
    def obtener_ip_local(self):
        """Obtiene la IP local de la máquina"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    async def verificar_servidor_registro(self):
        """Verifica si el servidor de registro está disponible"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.registry_host, self.registry_port),
                timeout=2.0
            )
            
            mensaje = {"action": "PING"}
            writer.write(json.dumps(mensaje).encode())
            await writer.drain()
            
            data = await asyncio.wait_for(reader.read(1024), timeout=2.0)
            response = json.loads(data.decode())
            
            writer.close()
            await writer.wait_closed()
            
            return response.get("status") == "success"
        except:
            return False
    
    async def iniciar_servidor_registro_background(self):
        """Inicia el servidor de registro en segundo plano"""
        print("\n🚀 Iniciando servidor de registro automáticamente...")
        
        try:
            self.registry_process = subprocess.Popen(
                [sys.executable, __file__, "registry"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Esperar a que el servidor esté listo
            for i in range(10):
                await asyncio.sleep(0.5)
                if await self.verificar_servidor_registro():
                    print("✅ Servidor de registro iniciado correctamente")
                    self.server_auto_started = True
                    return True
            
            print("⚠️  El servidor tardó en iniciar, pero continuando...")
            return True
            
        except Exception as e:
            print(f"⚠️  No se pudo iniciar el servidor automáticamente: {e}")
            return False
    
    async def comunicar_con_registro(self, mensaje):
        """Se comunica con el servidor de registro"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.registry_host, self.registry_port),
                timeout=5.0
            )
            
            writer.write(json.dumps(mensaje).encode())
            await writer.drain()
            
            data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            response = json.loads(data.decode())
            
            writer.close()
            await writer.wait_closed()
            
            return response
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Timeout al conectar con el servidor"}
        except Exception as e:
            return {"status": "error", "message": f"Error de conexión: {e}"}
    
    async def menu_principal(self):
        """Menú principal con verificación de servidor de registro"""
        # Verificar servidor de registro
        print("\n🔍 Verificando servidor de registro...")
        servidor_disponible = await self.verificar_servidor_registro()
        
        if not servidor_disponible:
            if await self.iniciar_servidor_registro_background():
                pass
            else:
                print("\n⚠️  No se pudo conectar al servidor de registro.")
                print("   Por favor, asegúrate de que esté activo e intenta de nuevo.")
                print("   También puedes usar el modo manual sin códigos.")
                
                opcion = input("\n👉 ¿Deseas iniciar en modo manual? (s/n): ").strip().lower()
                if opcion == "s":
                    return await self.menu_modo_manual()
                else:
                    print("\n👋 ¡Hasta luego!")
                    sys.exit(0)
            
        
        # Menú principal con códigos
        print("\n" + "="*70)
        print("🎲 PARCHÍS - SISTEMA DE LOBBY CON CÓDIGOS 🎲".center(70))
        print("="*70)
        print("\n📋 ¿Qué deseas hacer?")
        print("\n1. 🏠 Crear Sala (Obtener código de sala)")
        print("2. 🔗 Unirse con Código (Usar código de sala)")
        print("3. ⌨️  Conexión Manual (IP y Puerto directo)")
        print("4. ❌ Salir")
        print("\n" + "="*70)
        
        while True:
            try:
                opcion = input("\n👉 Elige una opción (1-4): ").strip()
                
                if opcion == "1":
                    await self.flujo_crear_lobby_con_codigo()
                    break
                elif opcion == "2":
                    await self.flujo_unirse_con_codigo()
                    break
                elif opcion == "3":
                    await self.flujo_unirse_lobby_manual()
                    break
                elif opcion == "4":
                    print("\n👋 ¡Hasta luego!")
                    await self.cerrar()
                    sys.exit(0)
                else:
                    print("⚠️  Opción inválida. Elige 1, 2, 3 o 4.")
            except KeyboardInterrupt:
                print("\n\n⚠️  Operación cancelada")
                await self.cerrar()
                sys.exit(0)
    
    async def menu_modo_manual(self):
        """Menú sin servidor de registro (modo original)"""
        print("\n" + "="*70)
        print("🎲 PARCHÍS - SISTEMA DE LOBBY (MODO MANUAL) 🎲".center(70))
        print("="*70)
        print("\n📋 ¿Qué deseas hacer?")
        print("\n1. 🏠 Crear Lobby (Ser HOST y jugar)")
        print("2. 🔗 Unirse a un Lobby (Conectarse con IP)")
        print("3. ❌ Salir")
        print("\n" + "="*70)
        
        while True:
            try:
                opcion = input("\n👉 Elige una opción (1-3): ").strip()
                
                if opcion == "1":
                    await self.flujo_crear_lobby_manual()
                    break
                elif opcion == "2":
                    await self.flujo_unirse_lobby_manual()
                    break
                elif opcion == "3":
                    print("\n👋 ¡Hasta luego!")
                    sys.exit(0)
                else:
                    print("⚠️  Opción inválida. Elige 1, 2 o 3.")
            except KeyboardInterrupt:
                print("\n\n⚠️  Operación cancelada")
                sys.exit(0)
    
    async def flujo_crear_lobby_con_codigo(self):
        """Crear lobby con código hexadecimal"""
        print("\n" + "🏠"*35)
        print("CREAR NUEVA SALA CON CÓDIGO".center(70))
        print("🏠"*35)
        
        nombre = input("\n👤 Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Host_{secrets.token_hex(2).upper()}"
            print(f"   (Usando nombre por defecto: {nombre})")
        
        puerto_input = input(f"\n🔌 Puerto (Enter para {self.puerto_default}): ").strip()
        puerto = int(puerto_input) if puerto_input.isdigit() else self.puerto_default
        
        ip_local = self.obtener_ip_local()
        self.hex_code = self.generar_codigo_hex()
        
        print("\n" + "⏳"*35)
        print("REGISTRANDO SALA...".center(70))
        print("⏳"*35)
        
        # Registrar en servidor central
        mensaje_registro = {
            "action": "REGISTER",
            "hex_code": self.hex_code,
            "game_port": puerto,
            "host_name": nombre,
            "ip_address": ip_local
        }
        
        response = await self.comunicar_con_registro(mensaje_registro)
        
        if response.get("status") == "success":
            print("\n" + "─"*70)
            print("✅ SALA CREADA EXITOSAMENTE".center(70))
            print("─"*70)
            print(f"\n🎫 CÓDIGO DE SALA: {self.hex_code}")
            print(f"👤 Tu nombre: {nombre}")
            print(f"📍 IP: {ip_local}:{puerto}")
            print("\n" + "─"*70)
            print("💡 INSTRUCCIONES PARA OTROS JUGADORES:")
            print(f"   1. Ejecutar el juego")
            print(f"   2. Elegir 'Unirse con Código'")
            print(f"   3. Ingresar el código: {self.hex_code}")
            print("─"*70)
            
            input("\n⏸️  Presiona ENTER para iniciar el servidor...")
            
            await self.iniciar_como_host(nombre, ip_local, puerto)
        else:
            print(f"\n❌ Error al registrar sala: {response.get('message')}")
            await asyncio.sleep(3)
            await self.menu_principal()
    
    async def flujo_unirse_con_codigo(self):
        """Unirse usando código hexadecimal"""
        print("\n" + "🔗"*35)
        print("UNIRSE CON CÓDIGO DE SALA".center(70))
        print("🔗"*35)
        
        nombre = input("\n👤 Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Jugador_{secrets.token_hex(2).upper()}"
            print(f"   (Usando nombre por defecto: {nombre})")
        
        hex_code = input("\n🎫 Ingresa el código de sala: ").strip().upper()
        
        if not hex_code:
            print("❌ Debes ingresar un código de sala")
            await asyncio.sleep(2)
            return await self.menu_principal()
        
        print(f"\n🔍 Buscando sala {hex_code}...")
        
        mensaje_consulta = {
            "action": "QUERY",
            "hex_code": hex_code
        }
        
        response = await self.comunicar_con_registro(mensaje_consulta)
        
        if response.get("status") == "success":
            lobby_info = response["lobby"]
            host_ip = lobby_info["ip"]
            host_port = lobby_info["port"]
            host_name = lobby_info["host_name"]
            
            print(f"\n✅ Sala encontrada!")
            print(f"   🏠 Host: {host_name}")
            print(f"   📍 {host_ip}:{host_port}")
            
            await self.iniciar_como_cliente(nombre, host_ip, host_port)
        else:
            print(f"\n❌ {response.get('message')}")
            print("\n💡 Verifica que:")
            print("   • El código sea correcto")
            print("   • La sala esté activa")
            await asyncio.sleep(3)
            await self.menu_principal()
    
    async def flujo_crear_lobby_manual(self):
        """Flujo original para crear lobby sin código"""
        print("\n" + "🏠"*35)
        print("CREAR NUEVO LOBBY".center(70))
        print("🏠"*35)
        
        nombre = input("\n👤 Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Host_{secrets.token_hex(2).upper()}"
            print(f"   (Usando nombre por defecto: {nombre})")
        
        puerto_input = input(f"\n🔌 Puerto (default: {self.puerto_default}): ").strip()
        puerto = int(puerto_input) if puerto_input.isdigit() else self.puerto_default
        
        ip_local = self.obtener_ip_local()
        
        print("\n" + "─"*70)
        print("📡 INFORMACIÓN DE TU LOBBY:".center(70))
        print("─"*70)
        print(f"📍 IP del HOST: {ip_local}")
        print(f"🔌 Puerto: {puerto}")
        print(f"🔗 Conexión completa: {ip_local}:{puerto}")
        print("─"*70)
        print("\n💡 INSTRUCCIONES PARA OTROS JUGADORES:")
        print(f"   1. Ejecutar el juego")
        print(f"   2. Elegir 'Unirse a Lobby'")
        print(f"   3. Ingresar IP: {ip_local}")
        print(f"   4. Ingresar Puerto: {puerto}")
        print("─"*70)
        
        input("\n⏸️  Presiona ENTER cuando estés listo para iniciar el servidor...")
        
        await self.iniciar_como_host(nombre, ip_local, puerto)
    
    async def flujo_unirse_lobby_manual(self):
        """Flujo original para unirse sin código"""
        print("\n" + "🔗"*35)
        print("UNIRSE A LOBBY EXISTENTE".center(70))
        print("🔗"*35)
        
        nombre = input("\n👤 Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Jugador_{secrets.token_hex(2).upper()}"
            print(f"   (Usando nombre por defecto: {nombre})")
        
        print("\n📡 Información de conexión:")
        host_ip = input("   IP del HOST (ej: 192.168.1.100): ").strip()
        
        if not host_ip:
            print("❌ Debes ingresar una IP válida")
            await asyncio.sleep(2)
            return await self.menu_principal()
        
        puerto_input = input(f"   Puerto (default: {self.puerto_default}): ").strip()
        puerto = int(puerto_input) if puerto_input.isdigit() else self.puerto_default
        
        print(f"\n🔗 Conectando a {host_ip}:{puerto}...")
        
        await self.iniciar_como_cliente(nombre, host_ip, puerto)
    
    async def iniciar_como_host(self, nombre, ip, puerto):
        """Inicia el servidor Y se conecta como cliente local"""
        print("\n" + "🚀"*35)
        print("INICIANDO SERVIDOR".center(70))
        print("🚀"*35)
        
        try:
            print(f"\n[1/3] Creando servidor en {ip}:{puerto}...")
            self.servidor = ParchisServer(host="0.0.0.0", port=puerto)
            self.es_host = True
            
            print("[2/3] Iniciando servidor en segundo plano...")
            servidor_task = asyncio.create_task(self.servidor.iniciar())
            
            await asyncio.sleep(2)
            
            print("[3/3] Conectándote como jugador HOST...")
            
            self.cliente = ParchisClient("localhost", puerto)
            
            if await self.cliente.conectar(nombre):
                print("\n" + "✅"*35)
                print("LOBBY CREADO EXITOSAMENTE".center(70))
                print("✅"*35)
                if self.hex_code:
                    print(f"\n🎫 Código de Sala: {self.hex_code}")
                print(f"📡 IP: {ip}:{puerto}")
                print(f"👤 Tu nombre: {nombre}")
                print(f"🏠 Rol: HOST + Jugador")
                print("\n⏳ Esperando que otros jugadores se unan...")
                print("💡 Cuando estén todos listos, podrás iniciar la partida\n")
                
                await self.cliente.ejecutar()
            else:
                print("❌ Error: No se pudo conectar al servidor local")
                self.servidor.detener()
                
        except Exception as e:
            print(f"\n❌ Error al iniciar como HOST: {e}")
            import traceback
            traceback.print_exc()
            if self.servidor:
                self.servidor.detener()
        finally:
            await self.cerrar()
    
    async def iniciar_como_cliente(self, nombre, host_ip, puerto):
        """Se conecta a un servidor existente como cliente"""
        print("\n" + "🔗"*35)
        print("CONECTANDO AL LOBBY".center(70))
        print("🔗"*35)
        
        try:
            print(f"\n[1/2] Creando cliente...")
            self.cliente = ParchisClient(host_ip, puerto)
            self.es_host = False
            
            print(f"[2/2] Conectando a {host_ip}:{puerto}...")
            
            if await self.cliente.conectar(nombre):
                print("\n" + "✅"*35)
                print("CONECTADO AL LOBBY EXITOSAMENTE".center(70))
                print("✅"*35)
                print(f"\n📡 Servidor: {host_ip}:{puerto}")
                print(f"👤 Tu nombre: {nombre}")
                print(f"🎮 Rol: Jugador")
                print("\n🎮 ¡A jugar!\n")
                
                await self.cliente.ejecutar()
            else:
                print("\n❌ No se pudo conectar al lobby")
                print("\n💡 Verifica que:")
                print("   • El HOST esté ejecutando el juego")
                print("   • La IP y puerto sean correctos")
                print("   • No haya firewall bloqueando la conexión")
                
                await asyncio.sleep(3)
                await self.menu_principal()
                
        except ConnectionRefusedError:
            print("\n❌ Conexión rechazada")
            print("💡 El servidor no está disponible en esa dirección")
            await asyncio.sleep(3)
            await self.menu_principal()
        except Exception as e:
            print(f"\n❌ Error al conectar: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(3)
            await self.menu_principal()
    
    async def cerrar(self):
        """Cierra servidor y cliente limpiamente"""
        print("\n🔄 Cerrando conexiones...")
        
        # Desregistrar del servidor central si somos host
        if self.es_host and self.hex_code:
            mensaje = {
                "action": "UNREGISTER",
                "hex_code": self.hex_code
            }
            try:
                await self.comunicar_con_registro(mensaje)
            except:
                pass
        
        if self.cliente:
            try:
                await self.cliente.desconectar()
            except Exception:
                pass
        
        if self.servidor:
            try:
                self.servidor.detener()
            except Exception:
                pass
        
        # Cerrar servidor de registro si lo iniciamos nosotros
        if self.server_auto_started and self.registry_process:
            print("🛑 Cerrando servidor de registro...")
            self.registry_process.terminate()
            try:
                self.registry_process.wait(timeout=5)
            except:
                self.registry_process.kill()
        
        print("✅ Sesión cerrada correctamente")


# ============================================================================
# MAIN
# ============================================================================

async def main_registry_server():
    """Inicia el servidor de registro"""
    server = RegistryServer(host="0.0.0.0", port=9000)
    await server.start()
    
async def main():
    """Función principal"""
    print("\n" + "🎮"*35)
    print("PARCHÍS DISTRIBUIDO - SISTEMA DE LOBBY".center(70))
    print("Versión 3.0 - Con Códigos Hexadecimales".center(70))
    print("🎮"*35)
    
    lobby_manager = LobbyManager(registry_host="localhost", registry_port=9000)
    
    try:
        await lobby_manager.menu_principal()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada...")
        await lobby_manager.cerrar()
        print("👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        await lobby_manager.cerrar()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "registry":
        print("🚀 Iniciando servidor de registro...")
        asyncio.run(main_registry_server())
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n\n👋 ¡Adiós!")