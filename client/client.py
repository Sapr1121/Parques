import socket

serv_IP = "192.168.1.7"
serv_PORT = 8001

try:
    client = socket.socket()
    client.connect((serv_IP, serv_PORT))
    print("Se ha conectado exitosamente")
    try:
        resp = client.recv(1024)
        if resp:
            print(f"Mensaje del servidor: {resp.decode()}")
        else:
            print("Estas dentro de la partida")

    except:
        print("Estas dentro de la partida")
    input("Presiona enter para salir de la partida")
    client.close()
except:
    print("Error al conectarse")

