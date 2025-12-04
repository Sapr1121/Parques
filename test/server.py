
import asyncio
import websockets

connected_clients = set()

async def handle_client(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            # Enviar el mensaje a todos los clientes conectados
            for client in connected_clients:
                if client != websocket:
                    await client.send(f"Otro usuario dice: {message}")
    except:
        print("Cliente desconectado.")
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Servidor WebSocket escuchando en ws://localhost:8765")
        await asyncio.Future()  # Mantener el servidor corriendo

asyncio.run(main())
