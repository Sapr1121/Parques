#!/usr/bin/env python3
import asyncio
import socket
import random
import string
import sys
from pathlib import Path

import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'client'))

# Ahora sí importar
from server import ParchisServer            
from client import ParchisClient



class LobbyManager:
    """Gestor de lobby que puede crear o unirse a partidas"""
    
    def __init__(self):
        self.servidor = None
        self.cliente = None
        self.es_host = False
        self.lobby_code = None
        self.puerto_default = 8001
        
    def obtener_ip_local(self):
        """Obtiene la IP local de la máquina"""
        try:
            # Crear socket temporal para obtener IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def generar_codigo_lobby(self):
        """Genera un código único para el lobby"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    async def menu_principal(self):
        """Menú principal para elegir modo"""
        print("\n" + "="*70)
        print("🎲 PARCHÍS - SISTEMA DE LOBBY 🎲".center(70))
        print("="*70)
        print("\n📋 ¿Qué deseas hacer?")
        print("\n1. 🏠 Crear Lobby (Ser HOST y jugar)")
        print("2. 🔗 Unirse a un Lobby (Conectarse a un HOST)")
        print("3. ❌ Salir")
        print("\n" + "="*70)
        
        while True:
            try:
                opcion = input("\n👉 Elige una opción (1-3): ").strip()
                
                if opcion == "1":
                    await self.flujo_crear_lobby()
                    break
                elif opcion == "2":
                    await self.flujo_unirse_lobby()
                    break
                elif opcion == "3":
                    print("\n👋 ¡Hasta luego!")
                    sys.exit(0)
                else:
                    print("⚠️  Opción inválida. Elige 1, 2 o 3.")
            except KeyboardInterrupt:
                print("\n\n⚠️  Operación cancelada")
                sys.exit(0)
    
    async def flujo_crear_lobby(self):
        """Flujo para crear un nuevo lobby"""
        print("\n" + "🏠"*35)
        print("CREAR NUEVO LOBBY".center(70))
        print("🏠"*35)
        
        # Obtener nombre del jugador
        nombre = input("\n👤 Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Host_{random.randint(100, 999)}"
            print(f"   (Usando nombre por defecto: {nombre})")
        
        # Configurar puerto
        puerto_input = input(f"\n🔌 Puerto (default: {self.puerto_default}): ").strip()
        puerto = int(puerto_input) if puerto_input.isdigit() else self.puerto_default
        
        # Obtener IP local
        ip_local = self.obtener_ip_local()
        
        # Generar código de lobby
        self.lobby_code = self.generar_codigo_lobby()
        
        print("\n" + "─"*70)
        print("📡 INFORMACIÓN DE TU LOBBY:".center(70))
        print("─"*70)
        print(f"🎫 Código de Lobby: {self.lobby_code}")
        print(f"📍 IP del HOST: {ip_local}")
        print(f"🔌 Puerto: {puerto}")
        print(f"🔗 Conexión completa: {ip_local}:{puerto}")
        print("─"*70)
        print("\n💡 INSTRUCCIONES PARA OTROS JUGADORES:")
        print(f"   1. Ejecutar: python hybrid_client.py")
        print(f"   2. Elegir opción 2 (Unirse a Lobby)")
        print(f"   3. Ingresar IP: {ip_local}")
        print(f"   4. Ingresar Puerto: {puerto}")
        print("─"*70)
        
        input("\n⏸️  Presiona ENTER cuando estés listo para iniciar el servidor...")
        
        # Iniciar servidor y cliente
        await self.iniciar_como_host(nombre, ip_local, puerto)
    
    async def flujo_unirse_lobby(self):
        """Flujo para unirse a un lobby existente"""
        print("\n" + "🔗"*35)
        print("UNIRSE A LOBBY EXISTENTE".center(70))
        print("🔗"*35)
        
        # Obtener nombre del jugador
        nombre = input("\n👤 Ingresa tu nombre: ").strip()
        if not nombre:
            nombre = f"Jugador_{random.randint(100, 999)}"
            print(f"   (Usando nombre por defecto: {nombre})")
        
        # Obtener IP del host
        print("\n📡 Información de conexión:")
        host_ip = input("   IP del HOST (ej: 192.168.1.100): ").strip()
        
        if not host_ip:
            print("❌ Debes ingresar una IP válida")
            await asyncio.sleep(2)
            return await self.menu_principal()
        
        # Obtener puerto
        puerto_input = input(f"   Puerto (default: {self.puerto_default}): ").strip()
        puerto = int(puerto_input) if puerto_input.isdigit() else self.puerto_default
        
        print(f"\n🔗 Conectando a {host_ip}:{puerto}...")
        
        # Conectar como cliente
        await self.iniciar_como_cliente(nombre, host_ip, puerto)
    
    async def iniciar_como_host(self, nombre, ip, puerto):
        """Inicia el servidor Y se conecta como cliente local"""
        print("\n" + "🚀"*35)
        print("INICIANDO SERVIDOR".center(70))
        print("🚀"*35)
        
        try:
            # Crear instancia del servidor
            print(f"\n[1/3] Creando servidor en {ip}:{puerto}...")
            self.servidor = ParchisServer(host="0.0.0.0", port=puerto)
            self.es_host = True
            
            # Iniciar servidor en background
            print("[2/3] Iniciando servidor en segundo plano...")
            servidor_task = asyncio.create_task(self.servidor.iniciar())
            
            # Esperar a que el servidor esté listo
            await asyncio.sleep(2)
            
            print("[3/3] Conectándote como jugador HOST...")
            
            # Crear cliente y conectar a servidor local
            self.cliente = ParchisClient("localhost", puerto)
            
            if await self.cliente.conectar(nombre):
                print("\n" + "✅"*35)
                print("LOBBY CREADO EXITOSAMENTE".center(70))
                print("✅"*35)
                print(f"\n🎫 Código de Lobby: {self.lobby_code}")
                print(f"📡 IP: {ip}:{puerto}")
                print(f"👤 Tu nombre: {nombre}")
                print(f"🏠 Rol: HOST")
                print("\n⏳ Esperando que otros jugadores se unan...")
                print("💡 Cuando estén todos listos, podrás iniciar la partida\n")
                
                # Ejecutar el cliente (esto bloquea hasta que termine)
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
            # Crear cliente
            print(f"\n[1/2] Creando cliente...")
            self.cliente = ParchisClient(host_ip, puerto)
            self.es_host = False
            
            print(f"[2/2] Conectando a {host_ip}:{puerto}...")
            
            # Intentar conectar
            if await self.cliente.conectar(nombre):
                print("\n" + "✅"*35)
                print("CONECTADO AL LOBBY EXITOSAMENTE".center(70))
                print("✅"*35)
                print(f"\n📡 Servidor: {host_ip}:{puerto}")
                print(f"👤 Tu nombre: {nombre}")
                print(f"🎮 Rol: Jugador")
                print("\n🎮 ¡A jugar!\n")
                
                # Ejecutar el cliente
                await self.cliente.ejecutar()
            else:
                print("\n❌ No se pudo conectar al lobby")
                print("\n💡 Verifica que:")
                print("   • El HOST esté ejecutando el juego")
                print("   • La IP y puerto sean correctos")
                print("   • No haya firewall bloqueando la conexión")
                print("   • Estén en la misma red (o tengas port forwarding configurado)")
                
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
        
        print("✅ Sesión cerrada correctamente")


async def main():
    """Función principal"""
    print("\n" + "🎮"*35)
    print("PARCHÍS DISTRIBUIDO - SISTEMA DE LOBBY".center(70))
    print("Versión 2.0 - Modo P2P Híbrido".center(70))
    print("🎮"*35)
    
    lobby_manager = LobbyManager()
    
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 ¡Adiós!")