from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from presentation.controller.blockchain_controller import BlockchainController

class OperazioniCompanyView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = BlockchainController()

        self.setWindowTitle("Operazioni registrate")

        self.layout = QVBoxLayout()
        self.info_label = QLabel(f"Operazioni per l'azienda:")
        self.list_widget = QListWidget()
        self.refresh_button = QPushButton("Aggiorna")

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.refresh_button)
        self.setLayout(self.layout)

        self.refresh_button.clicked.connect(self.carica_operazioni)

        self.carica_operazioni()

    def carica_operazioni(self):
        self.list_widget.clear()
        try:
            operazioni = self.controller.get_operazioni_company()
            if not operazioni:
                self.list_widget.addItem("Nessuna operazione registrata.")
            else:
                for op_id in operazioni:
                    self.list_widget.addItem(f"Operazione ID: {op_id}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel recupero delle operazioni:\n{str(e)}")
