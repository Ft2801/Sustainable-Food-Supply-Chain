# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton
)
from model.operation_estesa_model import OperazioneEstesaModel 
from presentation.view.vista_composizione_prodotto import VistaCreaProdottoTrasformato
from presentation.controller.company_controller import ControllerAzienda
from presentation.view.vista_aggiungi_operazione import AggiungiOperazioneView
from session import Session


class OperazioniAziendaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.id_azienda : int = Session().current_user["id_azienda"]
        self.role = Session().current_user["role"]
        self.controller = ControllerAzienda()
        

        self.operazioni : list[OperazioneEstesaModel]= self.controller.lista_operazioni(self.id_azienda) # Mock data
        self.operazioni_filtrate = self.operazioni.copy()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>ID azienda:</b> {self.id_azienda}"))

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtra operazioni...")
        self.filtro_input.textChanged.connect(self.filtra_operazioni)
        layout.addWidget(self.filtro_input)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(4)
        self.tabella.setHorizontalHeaderLabels(["Tipo", "Data", "Prodotto", "CO2"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)

        layout.addWidget(self.tabella)
        self.setLayout(layout)

        self.aggiorna_tabella()
        self.setWindowTitle("Operazioni Azienda")

        self.bottone_aggiungi = QPushButton("Aggiungi Operazione")
        self.bottone_aggiungi.clicked.connect(self.apri_aggiungi_operazione)
        layout.addWidget(self.bottone_aggiungi)

    def filtra_operazioni(self, testo):
        try:
            testo = testo.strip()
        except Exception as err :
            print(f"Errore durante il filtraggio delle operazioni: {err}")
            return
        if isinstance(testo, str):

            testo = testo.lower()
            self.operazioni_filtrate = [
                op for op in self.operazioni
                if testo in op.nome_operazione.lower() or testo in op.nome_prodotto.lower()
            ]
            self.aggiorna_tabella()

    def aggiorna_tabella(self):
        self.tabella.setRowCount(len(self.operazioni_filtrate))

        for row, oper in enumerate(self.operazioni_filtrate):
            # Colonna Tipo Operazione
            self.tabella.setItem(row, 0, QTableWidgetItem(oper.nome_operazione))
            
            # Colonna Data
            data_str = 'N/A'
            if hasattr(oper, 'data_operazione') and oper.data_operazione:
                if isinstance(oper.data_operazione, datetime.datetime) or isinstance(oper.data_operazione, datetime.date):
                    data_str = oper.data_operazione.strftime('%d/%m/%Y')
                else:
                    data_str = str(oper.data_operazione)
            self.tabella.setItem(row, 1, QTableWidgetItem(data_str))
            
            # Colonna Prodotto
            self.tabella.setItem(row, 2, QTableWidgetItem(oper.nome_prodotto if hasattr(oper, 'nome_prodotto') else ''))
            
            # Colonna CO2
            co2_str = str(oper.consumo_co2) if hasattr(oper, 'consumo_co2') else ''
            self.tabella.setItem(row, 3, QTableWidgetItem(co2_str))

    def apri_aggiungi_operazione(self):
        if Session().current_user["role"] == "Trasformatore":
            self.finestra_aggiungi = VistaCreaProdottoTrasformato(self)
        else:
            self.finestra_aggiungi = AggiungiOperazioneView(self)

        self.finestra_aggiungi.operazione_aggiunta.connect(self.ricarica_operazioni)
        self.finestra_aggiungi.exec_()  



    def ricarica_operazioni(self):
        self.operazioni = self.controller.lista_operazioni(self.id_azienda)
        self.filtra_operazioni(self.filtro_input.text())
