import sys
import socket
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class LoginWidget(QWidget):
    def __init__(self, parent, client_gui):
        super().__init__()

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Se Connecter", self)
        self.login_button.clicked.connect(client_gui.show_chat)

        self.signup_button = QPushButton("Créer un Compte", self)
        self.signup_button.clicked.connect(client_gui.show_signup)

        self.quit_button = QPushButton("Quitter", self)
        self.quit_button.clicked.connect(client_gui.close)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("Nom d'utilisateur:"), 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(QLabel("Mot de passe:"), 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(self.login_button, 2, 0, 1, 2)
        layout.addWidget(self.signup_button, 3, 0, 1, 2)
        layout.addWidget(self.quit_button, 4, 0, 1, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


class SignupWidget(QWidget):
    def __init__(self, parent, client_gui):
        super().__init__()

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.signup_button = QPushButton("Créer un Compte", self)
        self.signup_button.clicked.connect(client_gui.show_chat)

        self.back_button = QPushButton("Retour", self)
        self.back_button.clicked.connect(client_gui.show_login)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("Nom d'utilisateur:"), 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(QLabel("Mot de passe:"), 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(self.signup_button, 2, 0, 1, 2)
        layout.addWidget(self.back_button, 3, 0, 1, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client")
        self.setGeometry(100, 100, 400, 300)

        self.stacked_widget = QStackedWidget(self)
        self.login_widget = LoginWidget(self, self)
        self.signup_widget = SignupWidget(self, self)
        self.chat_widget = QWidget(self)

        self.chat_layout = QGridLayout(self.chat_widget)
        self.text_display = QTextEdit(self.chat_widget)
        self.text_display.setReadOnly(True)
        self.input_box = QLineEdit(self.chat_widget)
        self.send_button = QPushButton("Envoyer", self.chat_widget)
        self.send_button.clicked.connect(self.send_message)
        self.chat_layout.addWidget(self.text_display, 0, 0)
        self.chat_layout.addWidget(self.input_box, 1, 0)
        self.chat_layout.addWidget(self.send_button, 2, 0)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.signup_widget)
        self.stacked_widget.addWidget(self.chat_widget)

        self.server_address = ('127.0.0.1', 8864)
        self.client_socket = None
        self.receive_thread = None

        self.show_login()

    def show_login(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_signup(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_chat(self):
        self.stacked_widget.setCurrentIndex(2)
        self.connect_to_server()

    def connect_to_server(self):
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

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.text_display.append(message)
            except Exception as e:
                self.text_display.append(f"Erreur de réception de message")
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec())
