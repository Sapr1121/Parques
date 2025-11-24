#!/usr/bin/env python3
import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8001"
    print(f"🔌 Intentando conectar a {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado!")
            
            # Enviar mensaje de conexión
            mensaje = '{"tipo":"CONECTAR","nombre":"TestPlayer","color":"rojo"}'
            await websocket.send(mensaje)
            print(f"📤 Enviado: {mensaje}")
            
            # Esperar respuesta
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"📥 Respuesta: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
