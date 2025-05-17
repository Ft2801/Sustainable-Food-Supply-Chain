# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate, pyqtSignal
from presentation.controller.company_controller import ControllerAzienda


class VistaAggiungiAzioneCompensativa(QDialog):
    azione_aggiunta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Azione Compensativa")
        self.setMinimumWidth(300)
        self.controller = ControllerAzienda()  
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Descrizione dell'azione:"))
        self.input_descrizione = QLineEdit()
        layout.addWidget(self.input_descrizione)

        layout.addWidget(QLabel("CO₂ compensata (kg):"))
        self.input_co2 = QDoubleSpinBox()
        self.input_co2.setMinimum(0)
        self.input_co2.setMaximum(1000)
        self.input_co2.setDecimals(0)
        layout.addWidget(self.input_co2)

        layout.addWidget(QLabel("Data dell'azione:"))
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate())
        layout.addWidget(self.input_data)

        self.btn_salva = QPushButton("Salva Azione")
        self.btn_salva.clicked.connect(self.salva_azione)
        layout.addWidget(self.btn_salva)

        self.setLayout(layout)

    def salva_azione(self):
        descrizione = self.input_descrizione.text().strip()
        co2 = self.input_co2.value()
        data = self.input_data.date().toString("yyyy-MM-dd")

        if not descrizione:
            QMessageBox.warning(self, "Errore", "Inserisci una descrizione valida.")
            return

        if co2 <= 0:
            QMessageBox.warning(self, "Errore", "La CO₂ compensata deve essere maggiore di zero.")
            return

        try:
            self.controller.aggiungi_azione_compensativa(descrizione, co2, data)  
            QMessageBox.information(self, "Salvato", "Azione compensativa salvata con successo!")
            self.azione_aggiunta.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {e}")
