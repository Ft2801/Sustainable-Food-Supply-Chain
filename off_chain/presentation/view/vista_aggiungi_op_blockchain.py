from eth_account import Account
from eth_account.messages import encode_defunct
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox)
from presentation.controller.blockchain_controller import BlockchainController

class OperationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.controller = BlockchainController()

    def init_ui(self):
        self.setWindowTitle("Registrazione Operazione Blockchain")

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Chiave privata")
        self.key_input.setEchoMode(QLineEdit.Password)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descrizione operazione")

        self.op_type_input = QLineEdit()
        self.op_type_input.setPlaceholderText("Tipo operazione (es. 1)")

        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("ID lotto (0 se nessuno)")

        self.send_btn = QPushButton("Invia Operazione")
        self.send_btn.clicked.connect(self.handle_send)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Chiave Privata"))
        layout.addWidget(self.key_input)
        layout.addWidget(QLabel("Descrizione"))
        layout.addWidget(self.desc_input)
        layout.addWidget(QLabel("Tipo Operazione"))
        layout.addWidget(self.op_type_input)
        layout.addWidget(QLabel("Batch ID"))
        layout.addWidget(self.batch_input)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

    def handle_send(self):
        try:
            address = self.controller.get_address()
            private_key = self.key_input.text().strip()
            description = self.desc_input.text().strip()
            operation_type = int(self.op_type_input.text().strip())
            batch_id = int(self.batch_input.text().strip())

            account = Account.from_key(private_key)
            if account.address.lower() != address.lower():
                raise Exception("L'indirizzo non corrisponde alla chiave privata.")

            challenge = "Autenticazione per registrazione operazione"
            message = encode_defunct(text=challenge)
            signature = Account.sign_message(message, private_key=private_key).signature

            if self.controller.verifica_possesso_chiave(address, signature, challenge):
                tx_hash = self.controller.invia_operazione(private_key, operation_type, description, batch_id)
                QMessageBox.information(self, "Successo", f"Operazione inviata!\nHash: {tx_hash}")
            else:
                QMessageBox.critical(self, "Errore", "Autenticazione fallita.")

        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))