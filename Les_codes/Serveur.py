import socket
import threading
import os
import mysql.connector
from mysql.connector import Error
import time

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

    # Nouvelle commande pour annoncer l'arrêt du serveur
    announce_shutdown("Le serveur va s'arrêter dans 15 secondes.")

def announce_shutdown(message):
    for client_conn in list(authenticated_clients.values()):
        try:
            client_conn.send(f"SHUTDOWN_ANNOUNCE|{message}".encode())
        except Exception as e:
            print(f"Erreur d'envoi d'annonce d'arrêt du serveur à un client: {e}")

def acceuil_client(conn, address):
    Flag = False
    username = None

    print(f"Connexion établie avec {address}")

    while not Flag and username is None:
        try:
            conn.send("Veuillez vous connecter ou créer un compte.\n".encode())

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
                username, password = command_parts[1], command_parts[2]
                if is_valid_password(username, password):
                    conn.send("Connection réussi".encode())
                else:
                    conn.send("Il y a eu un problème lors de votre conncetion au serveur\nVeuillez réessayez".encode())
            elif command_parts[0] == 'QUIT':
                # Quitter
                conn.send("Déconnexion demandée.".encode())
                conn.close()
                clients.remove(conn)
                authenticated_clients.pop(username, None)
                Flag = True
            elif command_parts[0] == 'SHUTDOWN_ANNOUNCE':
                print("Annonce d'arrêt du serveur reçue.")
                conn.send("Arrêt du serveur confirmé.".encode())
                time.sleep(15)  # Attendre 15 secondes avant d'arrêter le serveur
                os._exit(0)
            else:
                conn.send("Commande non reconnue.".encode())

        except Exception as e:
            print(f"Le client {address} s'est déconnecté")
            clients.remove(conn)
            Flag = True

    if username is not None:
        authenticated_clients[username] = conn
        conn.send("Bienvenue sur Discussion, votre serveur de discussion interne !".encode())

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

    # Analyser la commande du message
    command_parts = message.split(" ")
    command = command_parts[0].lower()

    # Traiter la commande
    if command == 'kick':
        if len(command_parts) == 2:
            target_username = command_parts[1].replace('@', '')
            kick_user(target_username, sender_conn)
        else:
            sender_conn.send("Commande invalide. Format attendu : 'kick @username'".encode())

    elif command == 'ban':
        # Ajoutez ici le code pour traiter la commande 'ban'
        pass

    elif command == 'kill':
        # Planifier l'arrêt du serveur
        schedule_server_shutdown()

    else:
        # Envoyer le message aux clients
        for client_conn in active_clients:
            if client_conn != sender_conn:
                try:
                    client_conn.send(f"{username}: {message}".encode())
                except Exception as e:
                    print(f"Erreur d'envoi de message à un client: {e}")
                    authenticated_clients.pop(username, None)

def kick_user(target_username, sender_conn):
    # Vérifier si l'utilisateur cible est connecté
    if target_username in authenticated_clients:
        target_conn = authenticated_clients[target_username]
        target_conn.send("Vous avez été expulsé du serveur.".encode())
        target_conn.close()
        clients.remove(target_conn)
        authenticated_clients.pop(target_username, None)
    else:
        # Envoyer un message d'erreur au demandeur
        sender_conn.send(f"L'utilisateur {target_username} n'est pas connecté.".encode())

def schedule_server_shutdown():
    # Planifier l'arrêt du serveur après 15 secondes
    print("Le serveur va s'arrêter dans 15 secondes.")
    broadcast_to_clients("Le serveur va s'arrêter dans 15 secondes.")
    timer = threading.Timer(15, shutdown_server)
    timer.start()

def shutdown_server():
    # Arrêt du serveur
    print("Arrêt du serveur.")
    broadcast_to_clients("Le serveur s'arrête maintenant.")
    os._exit(0)

def broadcast_to_clients(message):
    # Envoyer le message à tous les clients
    for client_conn in authenticated_clients.values():
        try:
            client_conn.send(f"Serveur: {message}".encode())
        except Exception as e:
            print(f"Erreur d'envoi de message à un client: {e}")

if __name__ == "__main__":
    start_server()
