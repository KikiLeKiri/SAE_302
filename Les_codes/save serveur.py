import socket
import threading
import os
import mysql.connector
from mysql.connector import Error

# Configuration de la base de données
DB_HOST = 'localhost'
DB_USER = 'toto'
DB_PASSWORD = 'toto'
DB_DATABASE = 'discussion'

# Dictionnaire pour associer les connexions aux utilisateurs authentifiés
authenticated_clients = {}

# Liste pour stocker les connexions des clients
clients = []

# Fonction principale pour démarrer le serveur
def start_server():
    Flag = False
    port = 8864
    server_socket = socket.socket()
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    print("Le serveur est en attente de connexions...")
    
    # Attente de connexions
    while not Flag:
        conn, address = server_socket.accept()
        clients.append(conn)
        client_thread = threading.Thread(target=acceuil_client, args=(conn, address))
        client_thread.start()

    # Braodcast pour annoncer l'arrêt du serveur
    announce_shutdown("Le serveur va s'arrêter dans 15 secondes.")

# Fonction pour annoncer l'arrêt du serveur à tous les clients
def announce_shutdown(message):
    for client_conn in list(authenticated_clients.values()):
        try:
            client_conn.send(f"SHUTDOWN_ANNOUNCE|{message}".encode())
        except Exception as e:
            print(f"Erreur d'envoi d'annonce d'arrêt du serveur à un client: {e}")

# Fonction pour accueillir un client et gérer son authentification
def acceuil_client(conn, address):
    global authenticated_clients
    global clients

    Flag = False
    username = None
    creating_account = False

    print(f"Connexion établie avec {address}")
    conn.send("Veuillez vous connecter ou créer un compte.\n".encode())

    # Attente de l'authentification ou de la création de compte
    while not Flag and username is None:
        try:
            message = conn.recv(1024).decode()
            command_parts = message.split("|")

            if username is None:
                if command_parts[0] == 'AUTHENTICATE':
                    # Authentification
                    username, password = command_parts[1], command_parts[2]
                    if is_valid_password(username, password):
                        if not is_user_banned(username):
                            conn.send("Connection réussie".encode())
                            authenticated_clients[username] = conn
                            room_list = get_room_list()
                            conn.send(f"ROOM_LIST|{'|'.join(room_list)}".encode())
                        else:
                            conn.send("Vous êtes banni. Déconnexion.".encode())
                            conn.close()
                            Flag = True
                    else:
                        conn.send("Il y a eu un problème lors de votre connexion au serveur\nVeuillez réessayer".encode())
                        username = None  
                elif command_parts[0] == 'CREATE_ACCOUNT_TRIGGER' and not creating_account:
                    creating_account = True
                    username, password = command_parts[1], command_parts[2]
                    creating_account = False

                    if username is not None and password is not None:
                        # Enregistement de l'utilisateur dans la base de données
                        if save_user_to_database(username, password):
                            conn.send("CREATE_ACCOUNT_SUCCESS".encode())
                        else:
                            conn.send("CREATE_ACCOUNT_FAILURE".encode())
                    else:
                        conn.send("CREATE_ACCOUNT_FAILURE".encode())
                else:
                    conn.send("Veuillez vous connecter ou créer un compte.\n".encode())

            elif username is not None:
                authenticated_clients[username] = conn
                if 'ROOM_LIST' not in message:
                    conn.send("Bienvenue sur Discussion, votre serveur de discussion interne !".encode())

                    room_list = get_room_list()
                    conn.send(f"ROOM_LIST|{'|'.join(room_list)}".encode())

                # Gestion des messages du client authentifié
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

        except Exception as e:
            print(f"Le client {address} s'est déconnecté. Erreur : {e}")
            Flag = True

    # Gestion des messages du client après authentification
    if username is not None:
        authenticated_clients[username] = conn
        if 'ROOM_LIST' not in message:
            conn.send("Bienvenue sur Discussion, votre serveur de discussion interne !".encode())

            room_list = get_room_list()
            conn.send(f"ROOM_LIST|{'|'.join(room_list)}".encode())

        while not Flag:
            try:
                message = conn.recv(1024).decode()
                if not message:
                    print(f"Le client {username} s'est déconnecté.")
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

# Fonction pour authentifier un utilisateur
def authenticate_user(conn):
    try:
        username = None

        # Vérifie si l'utilisateur est banni
        while username is None or is_user_banned(username):
            conn.send("Authentification\nNom d'utilisateur: ".encode())
            username = conn.recv(1024).decode()

            # Vérifie l'existence de l'utilisateur dans la base de données
            if is_valid_user(username):
                if is_user_banned(username):
                    conn.send("Vous êtes banni. Déconnexion.".encode())
                    conn.close()
                    return None

                conn.send("Mot de passe: ".encode())
                password = conn.recv(1024).decode()

                # Vérifie le mot de passe dans la base de données
                if is_valid_password(username, password):
                    return username
                else:
                    conn.send("Mot de passe incorrect.".encode())
            else:
                conn.send("Nom d'utilisateur incorrect.".encode())

    except Exception as e:
        print(f"Erreur lors de l'authentification de l'utilisateur: {e}")
        return None

# Fonction pour créer un compte utilisateur
def create_account(conn):
    try:
        username, password = None, None

        # Vérifie si l'utilisateur existe déjà
        while username is None or is_valid_user(username):
            username = conn.recv(1024).decode()

            if is_valid_user(username):
                conn.send("Nom d'utilisateur déjà pris.".encode())
            else:
                conn.send("Mot de passe: ".encode())
                password = conn.recv(1024).decode()

                # Enregistre l'utilisateur dans la base de données
                if save_user_to_database(username, password):
                    return username, password
                else:
                    conn.send("CREATE_ACCOUNT_FAILURE".encode())

    except Exception as e:
        print(f"Erreur lors de la création de compte: {e}")
        return None, None

# Fonction pour vérifier si un utilisateur est valide
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

# Fonction pour vérifier si un mot de passe est valide
def is_valid_password(username, password):
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

# Fonction pour vérifier si un utilisateur est banni
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

# Fonction pour enregistrer un utilisateur dans la base de données
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

# Fonction pour gérer la communication entre les clients
def Communication(message, sender_conn, username):
    active_clients = list(authenticated_clients.values())

    command_parts = message.split(" ")
    command = command_parts[0].lower()

    # Commandes spécifiques
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
        if not is_user_banned(username):
                for client_conn in active_clients:
                    if client_conn != sender_conn:
                        try:
                            client_conn.send(f"{username}: {message}".encode())
                        except Exception as e:
                            print(f"Erreur d'envoi de message à un client: {e}")
                            authenticated_clients.pop(username, None)

        # Enregistre le message dans la base de données
        save_message_to_database(username, "Général", message)

# Fonction pour expulser un utilisateur du serveur
def kick_user(target_username, sender_conn):
    # Vérifie si l'utilisateur est connecté
    if target_username in authenticated_clients:
        target_conn = authenticated_clients[target_username]
        target_conn.send("Vous avez été expulsé du serveur.".encode())
        target_conn.close()
        clients.remove(target_conn)
        authenticated_clients.pop(target_username, None)
    else:
        sender_conn.send(f"L'utilisateur {target_username} n'est pas connecté.".encode())

# Fonction pour bannir un utilisateur
def ban_user(target_username):
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

        # Envoye d'un message aux autres personnes pour les informer d'un bannissement
        message_to_send = f"Serveur: L'utilisateur {target_username} a été banni du serveur."
        broadcast_to_clients(message_to_send)

    except Error as e:
        print(f"Erreur lors du bannissement de l'utilisateur: {e}")

# Fonction pour planifier l'arrêt du serveur
def schedule_server_shutdown():
    # Planifier l'arrêt du serveur 
    print("Le serveur va s'arrêter dans 15 secondes.")
    broadcast_to_clients("Le serveur va s'arrêter dans 15 secondes.")
    timer = threading.Timer(15, shutdown_server)
    timer.start()

# Fonction pour arrêter le serveur
def shutdown_server():
    # Arrêt du serveur
    print("Arrêt du serveur.")
    broadcast_to_clients("Le serveur s'arrête maintenant.")
    os._exit(0)

# Fonction pour diffuser un message à tous les clients
def broadcast_to_clients(message):
    active_clients = list(authenticated_clients.values())
    for client_conn in active_clients:
        try:
            client_conn.send(message.encode())
        except Exception as e:
            print(f"Erreur d'envoi de message à un client: {e}")

# Fonction pour obtenir la liste des salons disponibles
def get_room_list():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        cursor = connection.cursor()
        cursor.execute("SELECT Nom_Salon FROM Salons")
        room_list = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return room_list

    except Error as e:
        print(f"Erreur lors de la récupération de la liste des salons: {e}")
        return []

# Fonction pour rejoindre un salon
def join_room(username, room_name):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        cursor = connection.cursor()
        cursor.execute("SELECT ID_Salon FROM Salons WHERE Nom_Salon = %s", (room_name,))
        room_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO Utilisateurs_Salons (ID_Utilisateur, ID_Salon) VALUES "
                        "((SELECT ID_Utilisateur FROM Utilisateurs WHERE Nom_Utilisateur = %s), %s)",
                        (username, room_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True

    except Error as e:
        print(f"Erreur lors de l'adhésion à un salon: {e}")
        return False

# Fonction pour enregistrer un message dans la base de données
def save_message_to_database(username, room_name, content):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        cursor = connection.cursor()

        cursor.execute("SELECT ID_Utilisateur FROM Utilisateurs WHERE Nom_Utilisateur = %s", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT ID_Salon FROM Salons WHERE Nom_Salon = %s", (room_name,))
        room_id = cursor.fetchone()[0]

        # Insérer le message dans la table Messages
        cursor.execute("INSERT INTO Messages (ID_Utilisateur, ID_Salon, Contenu_Message, Date_Heure_Envoi) "
                       "VALUES (%s, %s, %s, NOW())", (user_id, room_id, content))

        connection.commit()
        cursor.close()
        connection.close()
        return True

    except Error as e:
        print(f"Erreur lors de l'enregistrement du message dans la base de données: {e}")
        return False

if __name__ == "__main__":
    start_server()