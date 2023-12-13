import socket
import threading

def receive_messages(sock):
    Flag = False
    while not Flag:
        try:
            message = sock.recv(1024).decode()
            print(message)
        except Exception as e:
            print(f"Erreur de réception de message: {str(e)}")
            break

def start_client():
    Flag = False 
    server_address = ('127.0.0.1', 8864)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(server_address)
        print("Connecté au serveur.")
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while not Flag:
            message = input("Saisissez un message (ou 'bye' pour quitter): ")
            client_socket.send(message.encode())

            if message.lower() == 'bye':
                break

        client_socket.send("bye".encode())

    except Exception as e:
        print(f"Erreur de connexion au serveur: {str(e)}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
