
import asyncio
import websockets

async def chat():
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("Conectado al servidor de chat.")
        while True:
            msg = input("Tú: ")
            await websocket.send(msg)
            response = await websocket.recv()
            print(response)

asyncio.run(chat())
