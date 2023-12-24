import socket
import threading
import os
import mysql.connector
from mysql.connector import Error

# Informations de connexion à la base de données MySQL
DB_HOST = 'localhost'
DB_USER = 'toto'
DB_PASSWORD = 'toto'
DB_DATABASE = 'discussion'

# Dictionnaire pour associer les connexions aux utilisateurs authentifiés
authenticated_clients = {}

# Liste pour stocker les connexions des clients
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
    username = None

    print(f"Connexion établie avec {address}")

    while not Flag and username is None:
        try:
            conn.send("Veuillez vous authentifier ou créer un compte.\n".encode())

            message = conn.recv(1024).decode()
            command_parts = message.split("|")

            if command_parts[0] == 'CREATE_ACCOUNT':
                # Création de compte
                username, password = create_account(conn)
                if username is not None and password is not None:
                    conn.send("CREATE_ACCOUNT_SUCCESS".encode())
                else:
                    conn.send("CREATE_ACCOUNT_FAILURE".encode())
            elif command_parts[0] == 'AUTHENTICATE':
                # Authentification
                username = authenticate_user(conn)
            elif command_parts[0] == 'QUIT':
                # Quitter
                conn.send("Déconnexion demandée.".encode())
                conn.close()
                clients.remove(conn)
                authenticated_clients.pop(username, None)
                Flag = True
            else:
                conn.send("Commande non reconnue.".encode())

        except Exception as e:
            print(f"Le client {address} s'est déconnecté")
            clients.remove(conn)
            Flag = True

    if username is not None:
        authenticated_clients[username] = conn
        conn.send("Authentification réussie. Bienvenue!".encode())

        while not Flag:
            try:
                message = conn.recv(1024).decode()
                if not message:
                    print(f"Le client {username} s'est déconnecté.")
                    conn.close()
                    clients.remove(conn)
                    authenticated_clients.pop(username, None)
                    Flag = True
                elif message.lower() == 'arret':
                    print("Client a demandé l'arrêt du serveur.")
                    conn.send("Arrêt du serveur.".encode())
                    conn.close()
                    os._exit(0)
                elif message.lower() == 'bye':
                    print(f"Le client {username} a demandé à se déconnecter.")
                    conn.send("Déconnexion demandée.".encode())
                    conn.close()
                    clients.remove(conn)
                    authenticated_clients.pop(username, None)
                    Flag = True
                else:
                    Communication(message, conn, username)
            except Exception as e:
                print(f"Le client {username} s'est déconnecté")
                clients.remove(conn)
                authenticated_clients.pop(username, None)
                Flag = True

def authenticate_user(conn):
    try:
        conn.send("Authentification\nNom d'utilisateur: ".encode())
        username = conn.recv(1024).decode()

        # Vérifier l'existence de l'utilisateur dans la base de données
        if is_valid_user(username):
            conn.send("Mot de passe: ".encode())
            password = conn.recv(1024).decode()

            # Vérifier le mot de passe dans la base de données
            if is_valid_password(username, password):
                return username
            else:
                conn.send("Mot de passe incorrect.".encode())
                return None
        else:
            conn.send("Nom d'utilisateur incorrect.".encode())
            return None

    except Exception as e:
        print(f"Erreur lors de l'authentification de l'utilisateur: {e}")
        return None

def create_account(conn):
    try:
        conn.send("Création de compte\nNom d'utilisateur: ".encode())
        username = conn.recv(1024).decode()

        # Vérifier si l'utilisateur existe déjà
        if is_valid_user(username):
            conn.send("Nom d'utilisateur déjà pris.".encode())
            return None, None

        conn.send("Mot de passe: ".encode())
        password = conn.recv(1024).decode()

        # Enregistrer l'utilisateur dans la base de données
        if save_user_to_database(username, password):
            conn.send("Compte créé avec succès.".encode())
            return username, password
        else:
            conn.send("Erreur lors de la création du compte.".encode())
            return None, None

    except Exception as e:
        print(f"Erreur lors de la création de compte: {e}")
        return None, None

def is_valid_user(username):
    # Vérifier si l'utilisateur existe dans la base de données
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Utilisateurs WHERE Nom_Utilisateur = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        return user is not None

    except Error as e:
        print(f"Erreur lors de la vérification de l'existence de l'utilisateur: {e}")
        return False

def is_valid_password(username, password):
    # Vérifier si le mot de passe correspond à l'utilisateur dans la base de données
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Utilisateurs WHERE Nom_Utilisateur = %s AND Mot_de_Passe = %s",
                        (username, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        return user is not None

    except Error as e:
        print(f"Erreur lors de la vérification du mot de passe: {e}")
        return False

def save_user_to_database(username, password):
    # Enregistrer l'utilisateur dans la base de données
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )

        cursor = connection.cursor()
        cursor.execute("INSERT INTO Utilisateurs (Nom_Utilisateur, Mot_de_Passe) VALUES (%s, %s)", (username, password))
        connection.commit()

        cursor.close()
        connection.close()

        return True

    except Error as e:
        print(f"Erreur lors de l'enregistrement de l'utilisateur dans la base de données: {e}")
        return False

def Communication(message, sender_conn, username):
    active_clients = list(authenticated_clients.values())

    for client_conn in active_clients:
        if client_conn != sender_conn:
            try:
                client_conn.send(f"{username}: {message}".encode())
            except Exception as e:
                print(f"Erreur d'envoi de message à un client: {e}")
                authenticated_clients.pop(username, None)

if __name__ == "__main__":
    start_server()
