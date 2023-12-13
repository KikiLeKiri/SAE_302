import sys
import threading
import socket
from PyQt6.QtWidgets import *


class LoginWidget(QWidget):
    def __init__(self, parent, client_gui):
        super().__init__()

        self.client_gui = client_gui

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Se Connecter", self)
        self.login_button.clicked.connect(self.client_gui.show_chat)
        
        self.signup_button = QPushButton("Créer un Compte", self)
        self.signup_button.clicked.connect(self.show_signup)

        self.quit_button = QPushButton("Quitter", self)
        self.quit_button.clicked.connect(self.client_gui.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Nom d'utilisateur:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Mot de passe:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)
        layout.addWidget(self.quit_button)

    def show_signup(self):
        self.client_gui.stacked_widget.setCurrentIndex(1)


class SignupWidget(QWidget):
    def __init__(self, parent, client_gui):
        super().__init__()

        self.client_gui = client_gui

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.signup_button = QPushButton("Créer un Compte", self)
        self.signup_button.clicked.connect(self.client_gui.show_chat)

        self.back_button = QPushButton("Retour", self)
        self.back_button.clicked.connect(self.show_login)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Nom d'utilisateur:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Mot de passe:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.signup_button)
        layout.addWidget(self.back_button)

    def show_login(self):
        self.client_gui.stacked_widget.setCurrentIndex(0)


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client")
        self.setGeometry(100, 100, 1000, 800)

        self.stacked_widget = QStackedWidget(self)
        self.login_widget = LoginWidget(self, self)
        self.signup_widget = SignupWidget(self, self)
        self.chat_widget = QWidget(self)
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.text_display = QTextEdit(self.chat_widget)
        self.text_display.setReadOnly(True)
        self.input_box = QLineEdit(self.chat_widget)
        self.send_button = QPushButton("Envoyer", self.chat_widget)
        self.send_button.clicked.connect(self.send_message)
        self.chat_layout.addWidget(self.text_display)
        self.chat_layout.addWidget(self.input_box)
        self.chat_layout.addWidget(self.send_button)
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
