# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QMessageBox
)
from presentation.controller.certification_controller import ControllerCertificatore


class VistaCertificazioniLotto(QWidget):
    def __init__(self, id_lotto, parent=None):
        super().__init__(parent)
        self.id_lotto = id_lotto
        self.controller = ControllerCertificatore()
        self.setWindowTitle(f"Certificazioni per Lotto {id_lotto}")
        self.init_ui()
        self.carica_certificazioni()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_info = QLabel(f"Certificazioni esistenti per il lotto {self.id_lotto}:")
        layout.addWidget(self.label_info)

        self.lista_certificazioni = QListWidget()
        layout.addWidget(self.lista_certificazioni)

        layout.addWidget(QLabel("Aggiungi nuova certificazione:"))

        self.input_descrizione = QLineEdit()
        self.input_descrizione.setPlaceholderText("Inserisci descrizione certificato...")
        layout.addWidget(self.input_descrizione)

        self.btn_aggiungi = QPushButton("Aggiungi certificazione")
        self.btn_aggiungi.clicked.connect(self.aggiungi_certificazione)
        layout.addWidget(self.btn_aggiungi)

        self.setLayout(layout)

    def carica_certificazioni(self):
        self.lista_certificazioni.clear()
        certificati = self.controller.get_certificati_lotto(self.id_lotto)
        for descrizione in certificati:
            item = QListWidgetItem(f"Azienda Certificatrice: {descrizione.nome_azienda} | Descrizione: {descrizione.descrizione} | Data: {descrizione.data} ")
            self.lista_certificazioni.addItem(item)

    def aggiungi_certificazione(self):
        descrizione = self.input_descrizione.text().strip()
        if not descrizione:
            QMessageBox.warning(self, "Errore", "La descrizione non può essere vuota.")
            return

        self.controller.aggiungi_certificazione(self.id_lotto, descrizione)
        QMessageBox.information(self, "Salvato", "Certificazione aggiunta con successo.")
        self.input_descrizione.clear()
        self.carica_certificazioni()
