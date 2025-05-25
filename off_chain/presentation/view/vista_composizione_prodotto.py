# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
     QVBoxLayout, QLabel, QLineEdit, QSpinBox, QListWidget, QListWidgetItem,
        QComboBox,  QPushButton, QInputDialog, QMessageBox, QDialog, 
)
from PyQt5.QtCore import Qt, pyqtSignal
from model.product_standard_model import ProductStandardModel
from model.prodotto_finito_model import ProdottoLottoModel
from presentation.controller.company_controller import ControllerAzienda

class VistaCreaProdottoTrasformato(QDialog):

    operazione_aggiunta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crea Nuovo Prodotto Trasformato")
        self.controller = ControllerAzienda()
        
        self.materie_prime : list[ProdottoLottoModel] = self.controller.get_materie_prime_magazzino_azienda()  


        self.quantita_usata_per_materia = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tipo di prodotto trasformato:"))
        self.combo_tipo_prodotto = QComboBox()
        self.tipologie_trasformati: list[ProductStandardModel] = self.controller.get_prodotti_standard()
        if self.tipologie_trasformati:
            for tipo in self.tipologie_trasformati:
                self.combo_tipo_prodotto.addItem(tipo.Nome_prodotto, tipo.Id_prodotto)
        layout.addWidget(self.combo_tipo_prodotto)

        layout.addWidget(QLabel("Descrizione aggiuntiva (opzionale):"))
        self.input_descrizione = QLineEdit()
        self.input_descrizione.setPlaceholderText("es. 'di pomodoro biologica'")
        self.input_descrizione.setMaxLength(50)
        layout.addWidget(self.input_descrizione)


        layout.addWidget(QLabel("Quantità prodotta:"))
        self.input_quantita = QSpinBox()
        self.input_quantita.setMinimum(1)
        layout.addWidget(self.input_quantita)

        layout.addWidget(QLabel("Seleziona materie prime da utilizzare:"))
        self.lista_materie = QListWidget()
        for materia_prima in self.materie_prime:
            item = QListWidgetItem(f"{materia_prima.nome} - Disponibile: {materia_prima.quantita}")  
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, materia_prima)  # ✅ Salva l'intero oggetto
            self.lista_materie.addItem(item)
        layout.addWidget(self.lista_materie)

        self.btn_quantita_usata = QPushButton("Specifica quantità usata per le materie selezionate")
        self.btn_quantita_usata.clicked.connect(self.specifica_quantita_usata)
        layout.addWidget(self.btn_quantita_usata)

        self.btn_salva = QPushButton("Crea Prodotto")
        self.btn_salva.clicked.connect(self.crea_prodotto)
        layout.addWidget(self.btn_salva)

        self.setLayout(layout)

    def specifica_quantita_usata(self):
        self.quantita_usata_per_materia.clear()
        for i in range(self.lista_materie.count()):
            item = self.lista_materie.item(i)
            if item.checkState() == Qt.Checked:
                materia: ProdottoLottoModel = item.data(Qt.UserRole)
                if isinstance(materia, ProdottoLottoModel):
                    quantita, succ = QInputDialog.getInt(
                        self,
                        "Quantità usata",
                        f"Quanta quantità usare di {materia.nome}?",
                        min=1,
                        max=int(materia.quantita),  # Convert int to int for QInputDialog.getInt()
                    )
                    if succ:
                        self.quantita_usata_per_materia[materia.id_prodotto] = (materia, quantita)

    def crea_prodotto(self):
        id_tipologia = self.combo_tipo_prodotto.currentData()
        descrizione = self.input_descrizione.text().strip()

        if not id_tipologia:
            QMessageBox.warning(self, "Errore", "Seleziona una tipologia di prodotto trasformato.")
            return

        quantita = self.input_quantita.value()


        if not self.quantita_usata_per_materia:
            QMessageBox.warning(self, "Errore", "Specifica le quantità delle materie prime selezionate.")
            return

        for _, (materia , quantita) in self.quantita_usata_per_materia.items():
            if isinstance(materia, ProdottoLottoModel):
                if quantita <= 0:
                    QMessageBox.warning(self, "Errore", f"La quantità usata deve essere maggiore di zero per {materia.nome}.")
                    return
                if quantita > materia.quantita:
                    QMessageBox.warning(self, "Errore", f"La quantità usata supera la disponibilità di {materia.nome}.")
                    return

        co2, suc = QInputDialog.getInt(
            self,
            "Consumo CO₂",
            "Inserisci il consumo di CO₂ (in kg):",
            min=0
        )
        if not suc:
            QMessageBox.information(self, "Annullato", "Creazione del prodotto annullata.")
            return

        self.controller.crea_prodotto_trasformato(id_tipologia, descrizione, quantita, self.quantita_usata_per_materia, co2)


        QMessageBox.information(self, "Salvato", "Prodotto trasformato creato con successo!")
        self.operazione_aggiunta.emit()
        self.accept()
