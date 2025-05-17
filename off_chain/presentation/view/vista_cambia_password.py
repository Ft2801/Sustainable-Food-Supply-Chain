# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from presentation.controller.credential_controller import ControllerAutenticazione


class VistaCambiaPassword(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ControllerAutenticazione()
        self.setWindowTitle("Cambia password")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Vecchia password:", self.old_password_input)
        form_layout.addRow("Nuova password:", self.new_password_input)
        form_layout.addRow("Conferma nuova password:", self.confirm_password_input)

        layout.addLayout(form_layout)

        self.change_button = QPushButton("Conferma cambio")
        self.change_button.clicked.connect(self.change_password)
        layout.addWidget(self.change_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def change_password(self):
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not self.controller.verifica_password(old_password):
            QMessageBox.critical(self, "Errore", "La vecchia password non è corretta.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Errore", "Le nuove password non coincidono.")
            return

        try:

            self.controller.cambia_password(new_password)
            QMessageBox.information(self, "Successo", "Password cambiata con successo.")
            self.close()
        except Exception as err:
            QMessageBox.warning(self, "Errore", f"{err}")

    
