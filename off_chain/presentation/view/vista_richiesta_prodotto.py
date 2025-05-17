# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QSpinBox, QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import  pyqtSignal
from model.info_product_for_choice_model import ProductForChoiceModel
from model.company_model import CompanyModel
from presentation.controller.company_controller import ControllerAzienda


class RichiestaProdottoView(QDialog):
    salva_richiesta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()
        
       
        self.prodotti: list[ProductForChoiceModel] = self.controller.get_prodotti_ordinabili()  
        
        
        self.aziende_trasporto : list[CompanyModel] = self.controller.get_aziende_trasporto()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Richiedi Prodotto")
        layout = QVBoxLayout()

        # Tabella prodotti
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(3)
        self.tabella.setHorizontalHeaderLabels(["Nome prodotto", "Azienda", "Qt. disponibile"])
        self.tabella.setSelectionBehavior(self.tabella.SelectRows)
        self.tabella.setSelectionMode(self.tabella.SingleSelection)
        self.tabella.setEditTriggers(QTableWidget.NoEditTriggers)

        self.carica_prodotti()
        layout.addWidget(QLabel("Seleziona un prodotto dalla lista:"))
        layout.addWidget(self.tabella)

        # Quantità richiesta
        layout.addWidget(QLabel("Quantità richiesta:"))
        self.input_quantita = QSpinBox()
        self.input_quantita.setMinimum(1)
        layout.addWidget(self.input_quantita)

        # Azienda di trasporto
        layout.addWidget(QLabel("Seleziona azienda di trasporto:"))
        self.combo_azienda = QComboBox()
        for azienda in self.aziende_trasporto:
            self.combo_azienda.addItem(azienda.nome, azienda.id_credenziali)  # Mostra nome, ma salva id
        layout.addWidget(self.combo_azienda)

        # Bottone richiesta
        self.btn_richiesta = QPushButton("Invia richiesta")
        self.btn_richiesta.clicked.connect(self.invia_richiesta)
        layout.addWidget(self.btn_richiesta)

        self.setLayout(layout)
        self.resize(500, 450)

    def carica_prodotti(self):
        self.tabella.setRowCount(len(self.prodotti))
        for row, prodotto in enumerate(self.prodotti):
            self.tabella.setItem(row, 0, QTableWidgetItem(prodotto.nome_prodotto))
            self.tabella.setItem(row, 1, QTableWidgetItem(prodotto.nome_azienda + str(prodotto.id_azienda)))  # Placeholder
            self.tabella.setItem(row, 2, QTableWidgetItem(str(prodotto.quantita))) # Placeholder
            self.tabella.setRowHeight(row, 30)

    def invia_richiesta(self):
        row = self.tabella.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Attenzione", "Seleziona un prodotto.")
            return

        prodotto = self.prodotti[row]
        quantita = self.input_quantita.value()

        if quantita > prodotto.quantita:  # Placeholder
            QMessageBox.warning(self, "Errore", "Quantità richiesta maggiore della disponibilità.")
            return

        id_azienda_trasporto = self.combo_azienda.currentData()
        nome_azienda = self.combo_azienda.currentText()

        try:
            self.controller.invia_richiesta(
                id_az_ricevente= prodotto.id_azienda,
                id_prodotto=prodotto.id_prodotto,
                quantita=quantita,
                id_az_trasporto=id_azienda_trasporto
            )
            QMessageBox.information(
                self, "Successo",
                f"Richiesta inviata con successo.\nTrasporto affidato a: {nome_azienda}."
            )
            
            self.salva_richiesta.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'invio della richiesta: {str(e)}")
