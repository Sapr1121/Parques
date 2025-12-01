#!/usr/bin/env python3
"""
Script de prueba para verificar la detección de IP
"""

import socket

def obtener_ip_local():
    """Obtiene la IP local de la máquina accesible en LAN"""
    try:
        # Método 1: Usando conexión UDP a un servidor externo
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        
        print(f"✅ Método 1 (UDP): {ip}")
        
        # Verificar que sea una IP LAN válida
        if ip.startswith(("192.168.", "10.", "172.")) and not ip.startswith("127."):
            print(f"   ✓ Es una IP LAN válida")
            return ip
        else:
            print(f"   ⚠️ No es una IP LAN típica")
        
        # Método 2: Buscar en todas las interfaces
        hostname = socket.gethostname()
        print(f"\n🖥️  Hostname: {hostname}")
        ip_list = socket.gethostbyname_ex(hostname)[2]
        
        print(f"\n📋 Todas las IPs encontradas:")
        for idx, ip in enumerate(ip_list, 1):
            print(f"   {idx}. {ip}")
            if ip.startswith(("192.168.", "10.")):
                print(f"      ✓ IP LAN válida")
            elif ip.startswith("127."):
                print(f"      ⚠️ Localhost")
            elif ip.startswith("172."):
                print(f"      ⚠️ Podría ser Docker/VPN")
        
        # Filtrar IPs LAN válidas
        for ip in ip_list:
            if ip.startswith(("192.168.", "10.")) and not ip.startswith("127."):
                print(f"\n✅ Seleccionada (Método 2): {ip}")
                return ip
        
        # Si no encontró nada, devolver la primera IP no-localhost
        for ip in ip_list:
            if not ip.startswith("127."):
                print(f"\n⚠️ Usando primera IP no-localhost: {ip}")
                return ip
        
        print(f"\n❌ No se encontró IP válida, usando localhost")
        return "127.0.0.1"
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return "127.0.0.1"

if __name__ == "__main__":
    print("="*70)
    print("🔍 PROBANDO DETECCIÓN DE IP LOCAL".center(70))
    print("="*70 + "\n")
    
    ip_final = obtener_ip_local()
    
    print("\n" + "="*70)
    print(f"🎯 IP FINAL SELECCIONADA: {ip_final}".center(70))
    print("="*70)
    
    print("\n💡 INSTRUCCIONES:")
    print(f"   • Esta es la IP que otros PCs usarán para conectarse")
    print(f"   • Compártela en tu LAN: {ip_final}")
    print(f"   • Los clientes deben poder hacer ping a esta IP")
    print(f"\n📝 Prueba desde otro PC:")
    print(f"   ping {ip_final}")
