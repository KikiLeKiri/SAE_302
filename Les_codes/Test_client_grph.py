import sys
import socket
import threading
from PyQt6.QtWidgets import *


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client")
        self.setGeometry(100, 100, 400, 300)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        self.input_box = QLineEdit(self)

        self.send_button = QPushButton("Envoyer", self)
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_display)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)

        self.server_address = ('127.0.0.1', 8864)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect(self.server_address)
            self.text_display.append("Connecté au serveur.")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            self.text_display.append(f"Erreur de connexion au serveur: {str(e)}")

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
                self.text_display.append(f"Erreur de réception de message: {str(e)}")
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec())
