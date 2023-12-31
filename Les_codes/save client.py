import sys
import socket
import threading
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QLabel, QDialog

class AuthenticationDialog(QDialog):
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
    close_signal = QtCore.pyqtSignal()
    ban_signal = QtCore.pyqtSignal()
    create_account_signal = QtCore.pyqtSignal(str, str)  # Signal pour créer un compte

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

        layout = QGridLayout(self)
        layout.addWidget(self.text_display, 0, 0, 1, 4)
        layout.addWidget(self.input_box, 1, 0, 1, 4)
        layout.addWidget(self.send_button, 2, 0, 1, 4)
        layout.addWidget(self.create_account_button, 3, 0)
        layout.addWidget(self.authenticate_button, 3, 1)
        layout.addWidget(self.quit_button, 3, 2, 1, 2)

        self.server_address = ('127.0.0.1', 8864)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect(self.server_address)
            self.text_display.append("Connecté au serveur.")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            self.text_display.append(f"Erreur de connexion au serveur")

        # Connecter le signal de création de compte au slot correspondant
        self.create_account_signal.connect(self.send_create_account_request)

    def send_message(self):
        message = self.input_box.text()
        self.client_socket.send(message.encode())
        self.input_box.clear()

    def create_account_dialog(self):
        auth_dialog = AuthenticationDialog()
        result = auth_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            username, password = auth_dialog.get_credentials()

            # Émettre le signal pour créer un compte
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

                # Décoder les messages et traiter en conséquence
                if message.startswith("CREATE_ACCOUNT_SUCCESS"):
                    self.text_display.append("Compte créé avec succès.")
                elif message.startswith("CREATE_ACCOUNT_FAILURE"):
                    self.text_display.append("Erreur lors de la création du compte.")
                elif message.startswith("Serveur:"):
                    self.text_display.append(message)
                    if "Le serveur s'arrête maintenant" in message:
                        # Émettre le signal pour fermer l'application
                        self.close_signal.emit()
                elif message.startswith("Banni:"):
                    # Le serveur indique que l'utilisateur est banni
                    self.text_display.append("Vous avez été banni du serveur.")
                    # Émettre le signal pour fermer l'application
                    self.ban_signal.emit()
                else:
                    self.text_display.append(message)

            except Exception as e:
                self.text_display.append(f"Erreur de réception de message")
                break

    def disconnect_from_server(self):
        try:
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

            # Attendre la réponse du serveur pour la création du compte
            response = self.client_socket.recv(1024).decode()

            if response == "CREATE_ACCOUNT_SUCCESS":
                self.text_display.append("Compte créé avec succès.")
            else:
                self.text_display.append("Erreur lors de la création du compte.")

        except Exception as e:
            self.text_display.append(f"Erreur lors de la création du compte: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()

    # Connecter le signal de fermeture au slot quit de l'application
    client_gui.close_signal.connect(app.quit)
    # Connecter le signal de bannissement au slot handle_ban de l'application
    client_gui.ban_signal.connect(client_gui.handle_ban)

    sys.exit(app.exec())