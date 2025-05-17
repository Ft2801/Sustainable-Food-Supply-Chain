# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt
from presentation.controller.company_controller import ControllerAzienda
from session import Session
from model.threshold_model import ThresholdModel


class SoglieAziendaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tipo_azienda : int = Session().current_user["role"]
        self.controller = ControllerAzienda()
        

        self.soglie : list[ThresholdModel]= self.controller.lista_soglie() # Mock data
        self.soglie_filtrate = self.soglie.copy()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>Soglie dell'azienda:</b> {self.tipo_azienda}"))

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtra soglie...")
        self.filtro_input.textChanged.connect(self.filtra_soglie)
        layout.addWidget(self.filtro_input)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(3)
        self.tabella.setHorizontalHeaderLabels(["Operazione", "Prodoto", "Soglia CO2","Tipo"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)

        layout.addWidget(self.tabella)
        self.setLayout(layout)

        self.aggiorna_tabella()
        self.setWindowTitle("Operazioni Azienda")

    

    def filtra_soglie(self, testo):
        testo = testo.lower()
        self.soglie_filtrate = [
            op for op in self.soglie
            if testo in op.Operazione.lower() or testo in op.Prodotto.lower() or testo in op.Soglia_Massima.lower()
        ]
        self.aggiorna_tabella()

    def aggiorna_tabella(self):
        self.tabella.setRowCount(len(self.soglie_filtrate))

        for row, oper in enumerate(self.soglie_filtrate):
            self.tabella.setItem(row, 0, QTableWidgetItem(oper.Tipo))
            self.tabella.setItem(row, 1, QTableWidgetItem(oper.Prodotto))
            self.tabella.setItem(row, 2, QTableWidgetItem(oper.Soglia_Massima))
            

            try:
                soglia = float(oper.Soglia_Massima)
                item_co2 = QTableWidgetItem(str(soglia))
                item_co2.setData(Qt.UserRole, soglia)  # Sorting numerico
            except Exception as err:
                print(f"[ERRORE parsing soglie]: {err} su {oper.Soglia_Massima}")
                item_co2 = QTableWidgetItem(oper.Soglia_Massima)
            self.tabella.setItem(row, 2, item_co2)



    def ricarica_soglie(self):
        self.soglie = self.controller.lista_soglie(self.id_azienda)
        self.filtra_soglie(self.filtro_input.text())
