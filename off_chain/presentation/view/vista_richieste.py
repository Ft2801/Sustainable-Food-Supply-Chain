# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QGroupBox, QHeaderView , QInputDialog
)

from presentation.controller.company_controller import ControllerAzienda
from presentation.view.vista_richiesta_prodotto import RichiestaProdottoView
from session import Session
from model.richiesta_model import RichiestaModel


class VisualizzaRichiesteView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()

    

        self.richieste_ricevute: list[RichiestaModel] = self.controller.get_richieste_ricevute()

        self.richieste_effettuate: list[RichiestaModel] = self.controller.get_richieste_effettuate()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gestione Richieste")

        layout = QVBoxLayout()

        # --- SEZIONE RICEVUTE ---
        if  Session().current_user["role"] != "Rivendiore":
            group_ricevute = QGroupBox("Richieste Ricevute")
            layout_ricevute = QVBoxLayout()

            self.tabella_ricevute = QTableWidget()
            self.tabella_ricevute.setColumnCount(6)  # 6 colonne!
            self.tabella_ricevute.setHorizontalHeaderLabels([
                "Azienda Destinataria", "Prodotto", "Quantità", "Stato Ricevente", "Stato Trasportatore", "Data"
            ])
            self.tabella_ricevute.setSelectionBehavior(QTableWidget.SelectRows)
            self.tabella_ricevute.setSelectionMode(QTableWidget.SingleSelection)
            self.tabella_ricevute.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tabella_ricevute.horizontalHeader().setStretchLastSection(True)  # Fa allungare l'ultima colonna
            self.tabella_ricevute.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            # Auto resize

            layout_ricevute.addWidget(self.tabella_ricevute)

            btn_layout = QHBoxLayout()
            self.btn_accetta = QPushButton("Accetta")
            self.btn_rifiuta = QPushButton("Rifiuta")
            self.btn_accetta.clicked.connect(self.accetta_richiesta)
            self.btn_rifiuta.clicked.connect(self.rifiuta_richiesta)
            btn_layout.addWidget(self.btn_accetta)
            btn_layout.addWidget(self.btn_rifiuta)

            layout_ricevute.addLayout(btn_layout)
            group_ricevute.setLayout(layout_ricevute)
            layout.addWidget(group_ricevute)

        if Session().current_user["role"] == "Trasformatore" or Session().current_user["role"] == "Rivenditore":
            
            group_effettuate = QGroupBox("Richieste Effettuate")
            layout_effettuate = QVBoxLayout()

            self.tabella_effettuate = QTableWidget()
            self.tabella_effettuate.setColumnCount(6)  # 6 colonne!
            self.tabella_effettuate.setHorizontalHeaderLabels([
                "Azienda Destinataria", "Prodotto", "Quantità", "Stato Ricevente", "Stato Trasportatore", "Data"
            ])
            self.tabella_effettuate.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tabella_effettuate.horizontalHeader().setStretchLastSection(True)
            self.tabella_ricevute.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.tabella_effettuate.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


            layout_effettuate.addWidget(self.tabella_effettuate)

            group_effettuate.setLayout(layout_effettuate)
            layout.addWidget(group_effettuate)
            self.carica_effettuate()
        
        

            self.bottone_aggiungi = QPushButton("Invia Richiesta")
            self.bottone_aggiungi.clicked.connect(self.apri_invia_richiesta)
            layout.addWidget(self.bottone_aggiungi)
        
        self.carica_ricevute()

        self.setLayout(layout)
        self.resize(1000, 700)

    def carica_ricevute(self):
        self.tabella_ricevute.setRowCount(len(self.richieste_ricevute))
        for row, richiesta in enumerate(self.richieste_ricevute):
            self.tabella_ricevute.setItem(row, 0, QTableWidgetItem(richiesta.nome_azienda_richiedente))
            self.tabella_ricevute.setItem(row, 1, QTableWidgetItem(richiesta.nome_prodotto))
            self.tabella_ricevute.setItem(row, 2, QTableWidgetItem(str(richiesta.quantita)))
            self.tabella_ricevute.setItem(row, 3, QTableWidgetItem(richiesta.stato_ricevente))
            self.tabella_ricevute.setItem(row, 4, QTableWidgetItem(richiesta.stato_trasportatore))
            self.tabella_ricevute.setItem(row, 5, QTableWidgetItem(str(richiesta.data)))

    def carica_effettuate(self):
        self.richieste_effettuate = self.controller.get_richieste_effettuate()
        self.tabella_effettuate.setRowCount(len(self.richieste_effettuate))
        for row, richiesta in enumerate(self.richieste_effettuate):
            self.tabella_effettuate.setItem(row, 0, QTableWidgetItem(richiesta.nome_azienda_ricevente))
            self.tabella_effettuate.setItem(row, 1, QTableWidgetItem(richiesta.nome_prodotto))
            self.tabella_effettuate.setItem(row, 2, QTableWidgetItem(str(richiesta.quantita)))
            self.tabella_effettuate.setItem(row, 3, QTableWidgetItem(richiesta.stato_ricevente))
            self.tabella_effettuate.setItem(row, 4, QTableWidgetItem(richiesta.stato_trasportatore))
            self.tabella_effettuate.setItem(row, 5, QTableWidgetItem(str(richiesta.data)))


    def accetta_richiesta(self):
        self._gestisci_richiesta("Accettata")

    def rifiuta_richiesta(self):
        self._gestisci_richiesta("Rifiutata")

    def _gestisci_richiesta(self, nuovo_stato):
        row = self.tabella_ricevute.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Attenzione", "Seleziona una richiesta.")
            return

        richiesta = self.richieste_ricevute[row]

        if Session().current_user["role"] == "Trasportatore":

            if richiesta.stato_trasportatore != "In attesa":
                QMessageBox.information(self, "Info", "Questa richiesta è già stata gestita.")
                return

            # --- Nuovo: chiedi CO2 emessa ---
            co2, succ = QInputDialog.getDouble(
                self, "CO₂ Emessa", "Inserisci la quantità di CO₂ emessa (kg):", decimals=2
            )

            if not succ:
                return  # L'utente ha annullato

            # --- Recupera id_prodotto e quantità dalla richiesta ---
            id_prodotto = richiesta.id_prodotto
            quantita = richiesta.quantita
            id_azienda_richiedente = richiesta.id_azienda_richiedente
            id_azienda_destinataria = richiesta.id_azienda_ricevente
            lotto_input = richiesta.id_lotto_input

            try:
                
                self.controller.salva_operazione_trasporto(
                    id_prodotto=id_prodotto,
                    quantita=quantita,
                    co2=co2,
                    id_azienda_richiedente=id_azienda_richiedente,
                    id_azienda_ricevente=id_azienda_destinataria,
                    id_lotto_input=lotto_input,
                )
            except Exception as err:
                QMessageBox.critical(self, "Errore", f"Errore nel salvataggio CO₂: {str(err)}")
                return


        try:
            self.controller.update_richiesta(
                id_richiesta=richiesta.id_richiesta,
                nuovo_stato=nuovo_stato
            )
            QMessageBox.information(self, "Successo", f"Richiesta accettata con successo.")

            # Ricarica dati
            #self.richieste_ricevute = self.controller.get_richieste_ricevute(self.id_azienda)
            self.carica_ricevute()
        except Exception as err:
            QMessageBox.critical(self, "Errore", f"Errore durante la gestione: {str(err)}")


    def apri_invia_richiesta(self):
        self.finestra_aggiungi = RichiestaProdottoView(self)
        self.finestra_aggiungi.salva_richiesta.connect(self.carica_effettuate)
        self.finestra_aggiungi.exec_()
