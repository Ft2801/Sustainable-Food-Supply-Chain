# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime

from model.compensation_action_model import CompensationActionModel 
from presentation.controller.company_controller import ControllerAzienda
from presentation.view.vista_aggiungi_az_compensativa import VistaAggiungiAzioneCompensativa
from session import Session


class AzioniAziendaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.id_azienda: int = Session().current_user["id_azienda"]
        self.controller = ControllerAzienda()

        self.azioni_compensative: list[CompensationActionModel] = self.controller.lista_azioni_compensative(self.id_azienda)
        self.azioni_compensative_filtrate = self.azioni_compensative.copy()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>ID azienda:</b> {self.id_azienda}"))

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtra azioni...")
        self.filtro_input.textChanged.connect(self.filtra_operazioni)
        layout.addWidget(self.filtro_input)

        # Filtro date
        self.data_da = QDateEdit()
        self.data_da.setCalendarPopup(True)
        self.data_da.setDate(QDate(2000, 1, 1))  # data bassa di default
        layout.addWidget(QLabel("Da:"))
        layout.addWidget(self.data_da)

        self.data_a = QDateEdit()
        self.data_a.setCalendarPopup(True)
        self.data_a.setDate(QDate.currentDate())  # oggi come default
        layout.addWidget(QLabel("A:"))
        layout.addWidget(self.data_a)

        self.data_da.dateChanged.connect(self.filtra_operazioni)
        self.data_a.dateChanged.connect(self.filtra_operazioni)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(3)
        self.tabella.setHorizontalHeaderLabels(["Tipo", "CO2 compensata", "Data"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)
        layout.addWidget(self.tabella)

        self.setLayout(layout)
        self.setWindowTitle("Azione Compensativa Azienda")

        self.bottone_aggiungi = QPushButton("Aggiungi Azione Compensativa")
        self.bottone_aggiungi.clicked.connect(self.apri_aggiungi_operazione)
        layout.addWidget(self.bottone_aggiungi)

        self.aggiorna_tabella()

    def filtra_operazioni(self):
        testo = self.filtro_input.text().lower()
        data_da = self.data_da.date().toPyDate()
        data_a = self.data_a.date().toPyDate()

        filtrate = []
        for op in self.azioni_compensative:
            try:
                # Converte la data dell'azione in oggetto datetime.date
                if isinstance(op.data_azione, str):
                    data_op = datetime.strptime(op.data_azione, "%Y-%m-%d").date()
                else:
                    data_op = op.data_azione

                if (testo in op.nome_azione.lower() or testo in str(op.co2_compensata).lower()) and data_da <= data_op <= data_a:
                    filtrate.append(op)
            except Exception as e:
                print(f"[ERRORE filtro]: {e} su record {op}")

        self.azioni_compensative_filtrate = filtrate
        self.aggiorna_tabella()

    def aggiorna_tabella(self):
        self.tabella.setRowCount(len(self.azioni_compensative_filtrate))

        for row, op in enumerate(self.azioni_compensative_filtrate):
            self.tabella.setItem(row, 0, QTableWidgetItem(op.nome_azione))

            try:
                co2_float = float(op.co2_compensata)
                item_co2 = QTableWidgetItem(str(co2_float))
                item_co2.setData(Qt.UserRole, co2_float)  # Sorting numerico
            except Exception as e:
                print(f"[ERRORE parsing CO2]: {e} su {op.co2_compensata}")
                item_co2 = QTableWidgetItem(op.co2_compensata)
            self.tabella.setItem(row, 1, item_co2)

            self.tabella.setItem(row, 2, QTableWidgetItem(str(op.data_azione)))

    def apri_aggiungi_operazione(self):
        self.finestra_aggiungi = VistaAggiungiAzioneCompensativa(self)
        self.finestra_aggiungi.azione_aggiunta.connect(self.ricarica_operazioni)
        self.finestra_aggiungi.exec_()

    def ricarica_operazioni(self):
        try:
            self.azioni_compensative = self.controller.lista_azioni_compensative(self.id_azienda)
            self.filtra_operazioni()
        except Exception as e:
            print(f"[ERRORE ricarica]: {e}")
