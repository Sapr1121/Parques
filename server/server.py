
import socket
from server.parchis import nada
import threading


clients = []
Max_client = 1


def management_client(client, addr):
    print(f"Client is connect: {addr}")
    try:
        while True:
            data = client.recv(1024)
            if not data:
                break
    except:
        pass
    finally:
        print(f"Cliente desconectado: {addr}")
        clients.remove(client)
        client.close()





serv = socket.socket()
serv.bind(("localhost", 8001))
serv.listen()
print("The server is listening...")

while True:
    client, addr = serv.accept()
    
    if len(clients) >= Max_client:
        print("Error... You can't connect")
        client.send(b"Servidor lleno no puedes entrar")
        client.close()
    else: 
        clients.append(client)
        thread = threading.Thread(target=management_client, args=(client, addr))
        thread.start()
        print(f"Client: {addr}")

