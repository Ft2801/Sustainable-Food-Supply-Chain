# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QHeaderView, QComboBox, QMessageBox
)
from presentation.view.vista_catena_prodotto import LottoTreeView
from presentation.controller.guest_controller import ControllerGuest
from model.prodotto_finito_cliente import ProdottoFinito


class ProdottiFinitiView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerGuest()
        self.prodotti : list[ProdottoFinito]= self.controller.get_prodotti()  # Tutti i prodotti
        self.prodotti_filtrati = self.prodotti.copy()  # Quelli attualmente visibili

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Visualizza Prodotti Finiti")
        layout = QVBoxLayout()

        # --- Sezione Filtri ---
        filtro_layout = QHBoxLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Filtra per nome...")
        self.input_nome.textChanged.connect(self.applica_filtri)  # Ricerca live
        filtro_layout.addWidget(QLabel("Nome:"))
        filtro_layout.addWidget(self.input_nome)

        self.input_lotto = QLineEdit()
        self.input_lotto.setPlaceholderText("Filtra per numero di lotto...")
        self.input_lotto.textChanged.connect(self.applica_filtri)  # Ricerca live
        filtro_layout.addWidget(QLabel("Numero Lotto:"))
        filtro_layout.addWidget(self.input_lotto)

        self.ordina_combo = QComboBox()
        self.ordina_combo.addItems(["Nessun Ordinamento", "CO₂ Crescente", "CO₂ Decrescente"])
        self.ordina_combo.currentIndexChanged.connect(self.applica_filtri)  # Cambia ordinamento live
        filtro_layout.addWidget(QLabel("Ordina:"))
        filtro_layout.addWidget(self.ordina_combo)

        self.bottone_reset = QPushButton("Reset Filtri")
        self.bottone_reset.clicked.connect(self.reset_filtri)
        filtro_layout.addWidget(self.bottone_reset)

        layout.addLayout(filtro_layout)

        # --- Tabella ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(3)
        self.tabella.setHorizontalHeaderLabels(["Nome", "Numero Lotto", "CO₂ Emessa (kg)"])
        self.tabella.horizontalHeader().setStretchLastSection(True)
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabella.cellDoubleClicked.connect(self.mostra_dettagli_prodotto)

        layout.addWidget(self.tabella)

        self.setLayout(layout)
        self.resize(900, 600)

        # Carica iniziale
        self.aggiorna_tabella()

    def aggiorna_tabella(self):
        self.tabella.setRowCount(len(self.prodotti_filtrati))

        for row, prodotto in enumerate(self.prodotti_filtrati):
            if isinstance(prodotto, ProdottoFinito):
                self.tabella.setItem(row, 0, QTableWidgetItem(prodotto.nome))
                self.tabella.setItem(row, 1, QTableWidgetItem(str(prodotto.numero_lotto)))
                self.tabella.setItem(row, 2, QTableWidgetItem(f"{prodotto.nome_azienda}"))

    def applica_filtri(self):
        nome_filtro = self.input_nome.text().lower()
        lotto_filtro = self.input_lotto.text().lower()
        

        # Filtra
        self.prodotti_filtrati = [
            p for p in self.prodotti
            
            if nome_filtro in p.nome.lower() and lotto_filtro in p.numero_lotto.lower()
        ]



        self.aggiorna_tabella()

    def reset_filtri(self):
        self.input_nome.clear()
        self.input_lotto.clear()
        self.ordina_combo.setCurrentIndex(0)
        self.prodotti_filtrati = self.prodotti.copy()
        self.aggiorna_tabella()

    def mostra_dettagli_prodotto(self, row):
        prodotto = self.prodotti_filtrati[row]

        if not isinstance(prodotto, ProdottoFinito):
            QMessageBox.warning(self, "Errore", "Dettagli non disponibili per questo prodotto.")
            return


        # Crea e mostra la nuova finestra
        self.finestra_storia = LottoTreeView(prodotto.numero_lotto)
        self.finestra_storia.show()
