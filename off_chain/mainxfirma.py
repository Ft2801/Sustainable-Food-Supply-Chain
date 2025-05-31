import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox
from model.credential_model import UserModel

class RegistroAzienda(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registrazione Azienda")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QFormLayout()

        self.nome = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(['Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore'])
        self.indirizzo = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        self.invia = QPushButton("Procedi con firma MetaMask")
        self.invia.clicked.connect(self.apri_html)

        self.layout.addRow("Nome Azienda:", self.nome)
        self.layout.addRow("Tipo Azienda:", self.tipo)
        self.layout.addRow("Indirizzo Fisico:", self.indirizzo)
        self.layout.addRow("Username:", self.username)
        self.layout.addRow("Password:", self.password)
        self.layout.addRow(self.invia)

        self.setLayout(self.layout)

    def apri_html(self):
        try:

            UserModel.validate_password(self.password.text())
            hash_psw = UserModel.hash_password(self.password.text())
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))
            return
        dati = {
            "nome": self.nome.text(),
            "tipo": self.tipo.currentText(),
            "indirizzo": self.indirizzo.text(),
            "username": self.username.text(),
            "password": hash_psw
        }

        url = f"http://localhost:5001/firma.html?nome={dati['nome']}&tipo={dati['tipo']}&indirizzo={dati['indirizzo']}&username={dati['username']}&password={dati['password']}"
        
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                subprocess.Popen([chrome_path, url])
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'apertura del browser: {str(e)}")
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistroAzienda()
    window.show()
    sys.exit(app.exec_())
