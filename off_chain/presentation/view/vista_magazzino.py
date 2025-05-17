# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit
)
from model.prodotto_finito_model import ProdottoLottoModel
from presentation.controller.company_controller import ControllerAzienda


class VisualizzaMagazzinoView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()

        self.prodotti_magazzino_completi: list[ProdottoLottoModel] = self.controller.get_materie_prime_magazzino_azienda()
        self.prodotti_finiti_magazzino: list[ProdottoLottoModel] = self.controller.get_prodotti_finiti_magazzino_azienda()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Magazzino Azienda")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Prodotti disponibili nel magazzino:"))

        # Campo di filtro per nome
        self.input_filtro_nome = QLineEdit()
        self.input_filtro_nome.setPlaceholderText("Filtra per nome prodotto...")
        self.input_filtro_nome.textChanged.connect(self.filtra_prodotti)
        layout.addWidget(self.input_filtro_nome)

        # Tabella Materie Prime
        layout.addWidget(QLabel("Materie Prime"))
        self.tabella_materie_prime = QTableWidget()
        self.tabella_materie_prime.setColumnCount(4)
        self.tabella_materie_prime.setHorizontalHeaderLabels([
            "Nome Prodotto", "Categoria", "Quantità Disponibile", "Unità di Misura"
        ])
        self.tabella_materie_prime.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabella_materie_prime)

        # Tabella Prodotti Finiti
        layout.addWidget(QLabel("Prodotti Finiti"))
        self.tabella_prodotti_finiti = QTableWidget()
        self.tabella_prodotti_finiti.setColumnCount(4)
        self.tabella_prodotti_finiti.setHorizontalHeaderLabels([
            "Nome Prodotto", "Categoria", "Quantità Disponibile", "Unità di Misura"
        ])
        self.tabella_prodotti_finiti.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabella_prodotti_finiti)

        self.setLayout(layout)
        self.resize(600, 600)

        self.filtra_prodotti()

    def filtra_prodotti(self):
        testo = self.input_filtro_nome.text().lower().strip()

        prodotti_materie = [
            p for p in self.prodotti_magazzino_completi
            if testo in p.nome.lower()
        ]
        prodotti_finiti = [
            p for p in self.prodotti_finiti_magazzino
            if testo in p.nome.lower()
        ]

        self.mostra_materie_prime(prodotti_materie)
        self.mostra_prodotti_finiti(prodotti_finiti)

    def mostra_materie_prime(self, prodotti: list[ProdottoLottoModel]):
        self.tabella_materie_prime.setRowCount(len(prodotti))
        for row, prodotto in enumerate(prodotti):
            self.tabella_materie_prime.setItem(row, 0, QTableWidgetItem(prodotto.nome))
            self.tabella_materie_prime.setItem(row, 1, QTableWidgetItem(prodotto.id_prodotto))
            self.tabella_materie_prime.setItem(row, 2, QTableWidgetItem(str(prodotto.quantita)))
            self.tabella_materie_prime.setItem(row, 3, QTableWidgetItem("kg"))  # Placeholder unità

    def mostra_prodotti_finiti(self, prodotti: list[ProdottoLottoModel]):
        self.tabella_prodotti_finiti.setRowCount(len(prodotti))
        for row, prodotto in enumerate(prodotti):
            self.tabella_prodotti_finiti.setItem(row, 0, QTableWidgetItem(prodotto.nome))
            self.tabella_prodotti_finiti.setItem(row, 1, QTableWidgetItem(prodotto.id_prodotto))
            self.tabella_prodotti_finiti.setItem(row, 2, QTableWidgetItem(str(prodotto.quantita)))
            self.tabella_prodotti_finiti.setItem(row, 3, QTableWidgetItem("kg"))  # Placeholder unità
