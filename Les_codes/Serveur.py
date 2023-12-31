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

    # commande pour annoncer l'arrêt du serveur
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
    creating_account = False

    print(f"Connexion établie avec {address}")

    if not creating_account:
        conn.send("Veuillez vous connecter ou créer un compte.\n".encode())

    while not Flag and username is None:
        try:
            message = conn.recv(1024).decode()
            command_parts = message.split("|")

            if command_parts[0] == 'CREATE_ACCOUNT_TRIGGER' and not creating_account:
                creating_account = True
                username, password = command_parts[1], command_parts[2]
                creating_account = False

                if username is not None and password is not None:
                    # Enregistrez l'utilisateur dans la base de données
                    if save_user_to_database(username, password):
                        conn.send("CREATE_ACCOUNT_SUCCESS".encode())
                    else:
                        conn.send("CREATE_ACCOUNT_FAILURE".encode())
                else:
                    conn.send("CREATE_ACCOUNT_FAILURE".encode())
            elif command_parts[0] == 'AUTHENTICATE':
                # Authentification
                username, password = command_parts[1], command_parts[2]
                if is_valid_password(username, password):
                    # Ajoutez cette vérification avant d'authentifier l'utilisateur
                    if not is_user_banned(username):
                        conn.send("Connection réussie".encode())
                    else:
                        conn.send("Vous êtes banni. Déconnexion.".encode())
                        conn.close()
                        Flag = True
                else:
                    conn.send("Il y a eu un problème lors de votre connexion au serveur\nVeuillez réessayer".encode())
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
                # Ajoutez cette vérification avant de traiter la commande
                if not is_user_banned(username):
                    conn.send("Commande non reconnue.".encode())
                else:
                    conn.send("Vous êtes banni. Déconnexion.".encode())
                    conn.close()
                    Flag = True

        except Exception as e:
            print(f"Le client {address} s'est déconnecté. Erreur : {e}")
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
        username = None

        # Vérifier si l'utilisateur est banni
        while username is None or is_user_banned(username):
            conn.send("Authentification\nNom d'utilisateur: ".encode())
            username = conn.recv(1024).decode()

            # Vérifier l'existence de l'utilisateur dans la base de données
            if is_valid_user(username):
                if is_user_banned(username):
                    conn.send("Vous êtes banni. Déconnexion.".encode())
                    conn.close()
                    return None

                conn.send("Mot de passe: ".encode())
                password = conn.recv(1024).decode()

                # Vérifier le mot de passe dans la base de données
                if is_valid_password(username, password):
                    return username
                else:
                    conn.send("Mot de passe incorrect.".encode())
            else:
                conn.send("Nom d'utilisateur incorrect.".encode())

    except Exception as e:
        print(f"Erreur lors de l'authentification de l'utilisateur: {e}")
        return None

def create_account(conn):
    try:
        username, password = None, None

        # Vérifier si l'utilisateur existe déjà
        while username is None or is_valid_user(username):
            username = conn.recv(1024).decode()

            if is_valid_user(username):
                conn.send("Nom d'utilisateur déjà pris.".encode())
            else:
                conn.send("Mot de passe: ".encode())
                password = conn.recv(1024).decode()

                # Enregistrer l'utilisateur dans la base de données
                if save_user_to_database(username, password):
                    return username, password
                else:
                    conn.send("CREATE_ACCOUNT_FAILURE".encode())

    except Exception as e:
        print(f"Erreur lors de la création de compte: {e}")
        return None, None



# Ajouter ces fonctions pour gérer la base de données
def is_valid_user(username):
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

def is_user_banned(username):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )

        cursor = connection.cursor()
        cursor.execute("SELECT Banni FROM Utilisateurs WHERE Nom_Utilisateur = %s", (username,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result and result[0] == 1
    except Error as e:
        print(f"Erreur lors de la vérification du statut de bannissement de l'utilisateur {username}: {e}")
        return False

def save_user_to_database(username, password):
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
        if len(command_parts) == 2:
            target_username = command_parts[1].replace('@', '')
            ban_user(target_username)
        else:
            sender_conn.send("Commande invalide. Format attendu : 'ban @username'".encode())

    elif command == 'kill':
        # Planifier l'arrêt du serveur
        schedule_server_shutdown()

    else:
        # Ajoutez cette vérification avant d'envoyer le message aux clients
        if not is_user_banned(username):
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

def ban_user(target_username):
    # Mettez à jour la base de données pour marquer l'utilisateur comme banni
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )

        cursor = connection.cursor()
        cursor.execute("UPDATE Utilisateurs SET Banni = TRUE WHERE Nom_Utilisateur = %s", (target_username,))
        connection.commit()

        cursor.close()
        connection.close()

        # Envoyer un message aux autres clients pour les informer du bannissement
        message_to_send = f"Serveur: L'utilisateur {target_username} a été banni du serveur."
        broadcast_to_clients(message_to_send)

    except Error as e:
        print(f"Erreur lors du bannissement de l'utilisateur: {e}")

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
    active_clients = list(authenticated_clients.values())
    for client_conn in active_clients:
        try:
            client_conn.send(message.encode())
        except Exception as e:
            print(f"Erreur d'envoi de message à un client: {e}")

if __name__ == "__main__":
    start_server()
