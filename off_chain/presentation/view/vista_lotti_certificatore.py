# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from model.lotto_for_cetification_model import LottoForCertificaion
from presentation.view.vista_aggiungi_certificazione import VistaCertificazioniLotto
from presentation.controller.certification_controller import ControllerCertificatore  # Sostituisci col tuo controller

class VistaRicercaLotti(QWidget):
    lotto_selezionato = pyqtSignal(int)  # Emit l'id del lotto selezionato

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ricerca Lotto")
        self.controller = ControllerCertificatore()  # Sostituisci con il tuo controller reale
        self.lotti: list[LottoForCertificaion] = self.controller.get_lotti_certificabili()  # Lista iniziale completa
        self.init_ui()
        self.finestre_aperte = []

    def init_ui(self):
        layout = QVBoxLayout()

        self.input_ricerca = QLineEdit()
        self.input_ricerca.setPlaceholderText("Inserisci ID lotto...")
        self.input_ricerca.textChanged.connect(self.aggiorna_lista)
        layout.addWidget(self.input_ricerca)

        self.lista_risultati = QListWidget()
        self.lista_risultati.itemClicked.connect(self.apri_dettagli_lotto)
        layout.addWidget(self.lista_risultati)

        self.setLayout(layout)

    def aggiorna_lista(self, testo):
        self.lista_risultati.clear()
        if not testo.strip():
            return

        for lotto in self.lotti:
            if testo.lower() in str(lotto.id_lotto).lower():
                item = QListWidgetItem(f"ID: {lotto.id_lotto} | Azienda: {lotto.nome_azienda} | Prodotto: {lotto.nome_prodotto} ")
                item.setData(Qt.UserRole, lotto.id_lotto)
                self.lista_risultati.addItem(item)

    

    def apri_dettagli_lotto(self, item):
        id_lotto = item.data(Qt.UserRole)
        finestra = VistaCertificazioniLotto(id_lotto)
        finestra.show()
        self.finestre_aperte.append(finestra)  
