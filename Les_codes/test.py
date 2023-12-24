import sys
import socket
import threading
from PyQt6.QtWidgets import *

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
        self.create_account_button.clicked.connect(self.create_account)

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

    def send_message(self):
        message = self.input_box.text()
        self.client_socket.send(message.encode())
        self.input_box.clear()

    def create_account(self):
        # Envoyer la commande au serveur pour créer un compte
        self.client_socket.send("CREATE_ACCOUNT".encode())

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec())
