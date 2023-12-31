import sys
import socket
import threading
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QLabel, QDialog, QComboBox

class AuthenticationDialog(QDialog):
    """
    Classe de fenêtre de dialogue pour l'authentification.
    Permet à l'utilisateur de saisir son nom d'utilisateur et son mot de passe.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Authentification")
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout(self)

        self.username_label = QLabel("Nom d'utilisateur:", self)
        self.username_input = QLineEdit(self)

        self.password_label = QLabel("Mot de passe:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Se connecter", self)
        self.login_button.clicked.connect(self.accept)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()

class ClientGUI(QWidget):
    """
    Classe représentant l'interface graphique du client.
    """

    close_signal = QtCore.pyqtSignal()
    ban_signal = QtCore.pyqtSignal()
    create_account_signal = QtCore.pyqtSignal(str, str)  # Signal pour créer un compte
    room_change_signal = QtCore.pyqtSignal(str)  # Signal pour changer de salon
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client")
        self.setGeometry(100, 100, 1000, 800)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        self.input_box = QLineEdit(self)

        self.send_button = QPushButton("Envoyer", self)
        self.send_button.clicked.connect(self.send_message)

        self.create_account_button = QPushButton("Créer un compte", self)
        self.create_account_button.clicked.connect(self.create_account_dialog)

        self.authenticate_button = QPushButton("Se connecter", self)
        self.authenticate_button.clicked.connect(self.authenticate)

        self.quit_button = QPushButton("Quitter", self)
        self.quit_button.clicked.connect(self.disconnect_from_server)

        self.room_list_label = QLabel("Salons disponibles:", self)
        self.room_list = QComboBox(self)
        self.room_list.currentIndexChanged.connect(self.join_room)

        layout = QGridLayout(self)
        layout.addWidget(self.text_display, 0, 0, 1, 4)
        layout.addWidget(self.input_box, 1, 0, 1, 4)
        layout.addWidget(self.send_button, 2, 0, 1, 4)
        layout.addWidget(self.create_account_button, 3, 0)
        layout.addWidget(self.authenticate_button, 3, 1)
        layout.addWidget(self.quit_button, 3, 2, 1, 2)
        layout.addWidget(self.room_list_label, 0, 4)
        layout.addWidget(self.room_list, 1, 4, 1, 1)

        self.server_address = ('127.0.0.1', 8864)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect(self.server_address)
            self.text_display.append("Connecté au serveur.")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            self.text_display.append(f"Erreur de connexion au serveur")

        # Connecte le signal de création de compte au slot correspondant
        self.create_account_signal.connect(self.send_create_account_request)
        # Connecte le signal de changement de salon au slot correspondant
        self.room_change_signal.connect(self.change_room)

    def send_message(self):
        message = self.input_box.text()
        # Envoye le message au serveur
        try:
            self.client_socket.send(message.encode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message au serveur: {e}")
        self.text_display.append(f"Vous: {message}")
        self.input_box.clear()
        
    def create_account_dialog(self):
        auth_dialog = AuthenticationDialog()
        result = auth_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            username, password = auth_dialog.get_credentials()

            self.create_account_signal.emit(username, password)

    def authenticate(self):
        # Utiliser la fenêtre de dialogue pour obtenir les informations d'authentification
        auth_dialog = AuthenticationDialog()
        result = auth_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            username, password = auth_dialog.get_credentials()

            # Envoyer la commande au serveur pour s'authentifier avec le nom d'utilisateur et le mot de passe
            self.client_socket.send(f"AUTHENTICATE|{username}|{password}".encode())

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                print(f"Message reçu: {message}")

                if message.startswith("Connection réussie"):
                    # L'utilisateur est connecté avec succès
                    self.text_display.append("Connexion réussie.")
                elif message.startswith("CREATE_ACCOUNT_SUCCESS"):
                    self.text_display.append("Compte créé avec succès.")
                elif message.startswith("Il y a eu un problème lors de votre connexion au serveur"):
                    self.text_display.append(message)
                elif message.startswith("CREATE_ACCOUNT_FAILURE"):
                    self.text_display.append("Erreur lors de la création du compte.")
                elif message.startswith("Serveur:"):
                    self.text_display.append(message)
                    if "Le serveur s'arrête maintenant" in message:
                        # Émettre le signal pour fermer l'application
                        self.close_signal.emit()
                        print("Fermeture de l'application signalée")
                elif message.startswith("Banni:"):
                    # Le serveur indique que l'utilisateur est banni
                    self.text_display.append("Vous avez été banni du serveur.")
                    # Émettre le signal pour fermer l'application
                    self.ban_signal.emit()
                    print("Fermeture de l'application signalée (banni)")
                elif message.startswith("ROOM_LIST"):
                    # Mise à jour de la liste des salons
                    room_list = message.split("|")[1:]
                    print(f"Liste des salons reçue du serveur: {room_list}")
                    self.update_room_list(room_list)
                else:
                    self.text_display.append(message)

            except Exception as e:
                print(f"Erreur de réception de message: {e}")
                break


    def disconnect_from_server(self):
        try:
            # Envoyer la commande de déconnexion au serveur
            self.client_socket.send("QUIT".encode())
            self.client_socket.close()
            self.text_display.append("Déconnecté du serveur.")
        except Exception as e:
            self.text_display.append(f"Erreur lors de la déconnexion du serveur.")
        self.close()

    def handle_ban(self):
        # Fermer la fenêtre de discussion en cas de bannissement
        self.close()

    def send_create_account_request(self, username, password):
        try:
            # Envoyer la commande au serveur pour créer un compte
            self.client_socket.send(f"CREATE_ACCOUNT_TRIGGER|{username}|{password}".encode())

            response = self.client_socket.recv(1024).decode()

            if response == "CREATE_ACCOUNT_SUCCESS":
                self.text_display.append("Compte créé avec succès.")

            QCoreApplication.processEvents()

        except Exception as e:
            self.text_display.append(f"Erreur lors de la création du compte: {e}")

    def join_room(self):
        # Émettre le signal pour changer de salon
        selected_room = self.room_list.currentText()
        self.room_change_signal.emit(selected_room)

    def change_room(self, room_name):
        # Changer de salon.
        self.text_display.append(f"Vous avez rejoint le salon : {room_name}")
    
    def update_room_list(self, room_list):
        # Mettre à jour la liste déroulante des salons
        self.room_list.clear()
        self.room_list.addItems(room_list)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()

    # Connecter le signal de fermeture au slot quit de l'application
    client_gui.close_signal.connect(app.quit)
    # Connecter le signal de bannissement au slot handle_ban de l'application
    client_gui.ban_signal.connect(client_gui.handle_ban)

    sys.exit(app.exec())