import sys
import socket
import threading
from PyQt6.QtWidgets import *

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

        self.authenticate_button = QPushButton("Se connceter", self)
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
        # Envoyer la commande au serveur pour s'authentifier
        self.client_socket.send("AUTHENTICATE".encode())

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

    # Fermer la connexion au serveur
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