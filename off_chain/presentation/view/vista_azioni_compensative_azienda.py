# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDateEdit, QMessageBox, QHBoxLayout, QInputDialog
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import sqlite3

from model.compensation_action_model import CompensationActionModel 
from presentation.controller.company_controller import ControllerAzienda
from presentation.controller.blockchain_controller import BlockchainController
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
        self.tabella.setColumnCount(4)  # Aggiunta colonna per lo stato blockchain
        self.tabella.setHorizontalHeaderLabels(["Tipo", "CO2 compensata", "Data", "Su Blockchain"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)
        layout.addWidget(self.tabella)

        self.setLayout(layout)
        self.setWindowTitle("Azione Compensativa Azienda")

        # Crea un layout orizzontale per i bottoni
        button_layout = QHBoxLayout()
        
        # Bottone per aggiungere azioni compensative
        self.bottone_aggiungi = QPushButton("Aggiungi Azione Compensativa")
        self.bottone_aggiungi.clicked.connect(self.apri_aggiungi_operazione)
        button_layout.addWidget(self.bottone_aggiungi)
        
        # Bottone per registrare azioni sulla blockchain
        self.bottone_deploy = QPushButton("Registra su Blockchain")
        self.bottone_deploy.clicked.connect(self.deploy_azione_blockchain)
        button_layout.addWidget(self.bottone_deploy)
        
        # Aggiungi il layout dei bottoni al layout principale
        layout.addLayout(button_layout)

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
            
            # Colonna Stato Blockchain
            blockchain_status = "Sì" if hasattr(op, 'blockchain_registered') and op.blockchain_registered else "No"
            item = QTableWidgetItem(blockchain_status)
            # Imposta il colore di sfondo in base allo stato
            if blockchain_status == "Sì":
                item.setBackground(QColor(200, 255, 200))  # Verde chiaro
            else:
                item.setBackground(QColor(255, 200, 200))  # Rosso chiaro
            self.tabella.setItem(row, 3, item)

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

    def deploy_azione_blockchain(self):
        # Verifica se è stata selezionata un'azione compensativa
        selected_items = self.tabella.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nessuna selezione", "Seleziona un'azione compensativa dalla tabella prima di procedere.")
            return
        
        # Ottieni la riga selezionata
        selected_row = selected_items[0].row()
        
        # Recupera l'azione selezionata
        azione = self.azioni_compensative_filtrate[selected_row]
        
        # Chiedi conferma all'utente
        risposta = QMessageBox.question(
            self, 
            "Conferma registrazione", 
            f"Vuoi registrare l'azione compensativa '{azione.nome_azione}' sulla blockchain?\n\n" 
            f"CO2 compensata: {azione.co2_compensata}\n" 
            f"Data: {azione.data_azione}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if risposta == QMessageBox.No:
            return
        
        try:
            # Ottieni la chiave privata dell'utente
            blockchain_controller = BlockchainController()
            
            # Ottieni la chiave privata
            private_key, ok = QInputDialog.getText(
                self, 
                "Chiave privata", 
                "Inserisci la tua chiave privata per firmare la transazione:",
                QLineEdit.Password
            )
            
            if not ok or not private_key:
                return
            
            # Crea la descrizione dell'azione compensativa
            description = f"Azione compensativa: {azione.nome_azione}, CO2 compensata: {azione.co2_compensata}"
            
            # Invia l'azione alla blockchain usando il metodo specifico per azioni compensative
            tx_hash = blockchain_controller.invia_azione_compensativa(
                private_key,
                azione.nome_azione,  # Tipo di azione compensativa
                azione.co2_compensata,  # Quantità di CO2 compensata
                description,
                azione.id_azione  # Passa l'ID dell'azione per aggiornare lo stato
            )
            
            # Lo stato dell'azione nel database viene aggiornato automaticamente dal metodo invia_azione_compensativa
            
            # Mostra conferma all'utente
            QMessageBox.information(
                self,
                "Azione registrata",
                f"L'azione compensativa è stata registrata sulla blockchain con successo!\n\nHash transazione: {tx_hash}"
            )
            
            # Ricarica le azioni per mostrare lo stato aggiornato
            self.ricarica_operazioni()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Si è verificato un errore durante la registrazione dell'azione sulla blockchain:\n{str(e)}"
            )
