from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from presentation.controller.blockchain_controller import BlockchainController

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton
)

class OperazioniCompanyView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messaggi registrati sulla blockchain")
        self.resize(600, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Messaggi:")
        self.layout.addWidget(self.label)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.button = QPushButton("Aggiorna messaggi")
        self.button.clicked.connect(self.load_data)
        self.layout.addWidget(self.button)

        self.load_data()

    def load_data(self):
        try:
            controller = BlockchainController()
            messaggi = controller.get_all_comp()
            self.table.setRowCount(len(messaggi))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["ido","idin", "qt"])

            for i, m in enumerate(messaggi):
                self.table.setItem(i, 0, QTableWidgetItem(str(m[0])))  # tipo
                self.table.setItem(i, 1, QTableWidgetItem(str(m[1])))
                self.table.setItem(i, 2, QTableWidgetItem(str(m[2])))


            
            print(str(controller.getComposizione(4)))
            print(str(controller.getComposizione(3)))
            print(str(controller.getComposizione(2)))
                

        except Exception as e:
            self.label.setText(f"Errore: {str(e)}")