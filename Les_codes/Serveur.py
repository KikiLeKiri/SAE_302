import socket
import threading
import os

clients = []

def start_server():
    Flag = False
    port = 8864
    server_socket = socket.socket()
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    print("Le serveur est en attente de connexions...")
    while not Flag:
        conn, address = server_socket.accept()
        clients.append(conn)
        client_thread = threading.Thread(target=acceuil_client, args=(conn, address))
        client_thread.start()

def acceuil_client(conn, address):
    Flag = False
    print(f"Connexion établie avec {address}")
    while not Flag:
        try:
            message = conn.recv(1024).decode()
            if not message:
                print(f"Le client {address} s'est déconnecté.")
                conn.close()
                clients.remove(conn)
                Flag = True 
            elif message.lower() == 'arret':
                print("Client a demandé l'arrêt du serveur.")
                conn.send("Arrêt du serveur.".encode())
                conn.close()
                os._exit(0)
            elif message.lower() == 'bye':
                print(f"Le client {address} a demandé à se déconnecter.")
                conn.send("Déconnexion demandée.".encode())
                conn.close()
                clients.remove(conn)
                Flag = True
            else:
                Communication(message, conn)
        except Exception as e:
            print(f"Le client {address} s'est déconnecté")
            clients.remove(conn)
            Flag = True

def Communication(message, sender_conn):
    active_clients = list(clients)  
    for client_conn in active_clients:
        if client_conn != sender_conn:
            try:
                client_conn.send(message.encode())
            except Exception as e:
                print(f"Erreur d'envoi de message à un client: ")
                clients.remove(client_conn)

if __name__ == "__main__":
    start_server()

