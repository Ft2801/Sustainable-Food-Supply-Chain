# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QColor
from model.operation_estesa_model import OperazioneEstesaModel 
from presentation.view.vista_composizione_prodotto import VistaCreaProdottoTrasformato
from presentation.controller.company_controller import ControllerAzienda
from presentation.view.vista_aggiungi_operazione import AggiungiOperazioneView
from presentation.controller.blockchain_controller import BlockchainController
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
        self.tabella.setColumnCount(5)  # Aggiunto una colonna per lo stato blockchain
        self.tabella.setHorizontalHeaderLabels(["Tipo", "Data", "Prodotto", "CO2", "Su Blockchain"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)

        layout.addWidget(self.tabella)
        self.setLayout(layout)

        self.aggiorna_tabella()
        self.setWindowTitle("Operazioni Azienda")

        # Crea un layout orizzontale per i bottoni
        button_layout = QHBoxLayout()
        
        # Bottone per aggiungere operazioni
        self.bottone_aggiungi = QPushButton("Aggiungi Operazione")
        self.bottone_aggiungi.clicked.connect(self.apri_aggiungi_operazione)
        button_layout.addWidget(self.bottone_aggiungi)
        
        # Bottone per deployare operazioni sulla blockchain
        self.bottone_deploy = QPushButton("Registra su Blockchain")
        self.bottone_deploy.clicked.connect(self.deploy_operazione_blockchain)
        button_layout.addWidget(self.bottone_deploy)
        
        # Aggiungi il layout dei bottoni al layout principale
        layout.addLayout(button_layout)

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
            
            # Colonna Stato Blockchain
            blockchain_status = "Sì" if hasattr(oper, 'blockchain_registered') and oper.blockchain_registered else "No"
            item = QTableWidgetItem(blockchain_status)
            # Imposta il colore di sfondo in base allo stato
            if blockchain_status == "Sì":
                item.setBackground(QColor(200, 255, 200))  # Verde chiaro
            else:
                item.setBackground(QColor(255, 200, 200))  # Rosso chiaro
            self.tabella.setItem(row, 4, item)

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
        
    def deploy_operazione_blockchain(self):
        # Verifica se è stata selezionata un'operazione
        selected_items = self.tabella.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nessuna selezione", "Seleziona un'operazione dalla tabella prima di procedere.")
            return
        
        # Ottieni la riga selezionata
        selected_row = selected_items[0].row()
        
        # Recupera l'operazione selezionata
        operazione = self.operazioni_filtrate[selected_row]
        
        # Chiedi conferma all'utente
        risposta = QMessageBox.question(
            self, 
            "Conferma registrazione", 
            f"Vuoi registrare l'operazione '{operazione.nome_operazione}' sulla blockchain?\n\n" 
            f"Prodotto: {operazione.nome_prodotto}\n" 
            f"Data: {operazione.data_operazione}\n" 
            f"CO2: {operazione.consumo_co2}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if risposta == QMessageBox.No:
            return
        
        try:
            # Ottieni la chiave privata dell'utente
            # In un'applicazione reale, questo dovrebbe essere gestito in modo più sicuro
            blockchain_controller = BlockchainController()
            
            # Ottieni la chiave privata (in un'app reale, questo dovrebbe essere più sicuro)
            private_key, ok = QInputDialog.getText(
                self, 
                "Chiave privata", 
                "Inserisci la tua chiave privata per firmare la transazione:",
                QLineEdit.Password
            )
            
            if not ok or not private_key:
                return
            
            # Mappa il tipo di operazione al valore enum usato nel contratto
            operation_type_map = {
                "Produzione": 0,  # OperationType.Production
                "Trasformazione": 1,  # OperationType.Processing
                "Trasporto": 2,  # OperationType.Transport
                "Vendita": 3   # OperationType.Sale
            }
            
            # Determina il tipo di operazione
            operation_type = operation_type_map.get(operazione.nome_operazione, 0)
            
            # Crea la descrizione dell'operazione
            description = f"Prodotto: {operazione.nome_prodotto}, CO2: {operazione.consumo_co2}"
            
            # Batch ID (0 se non associato a un lotto)
            batch_id = 0  # Modifica se hai un ID lotto associato all'operazione
            
            # Invia l'operazione alla blockchain
            tx_hash = blockchain_controller.invia_operazione(
                private_key,
                operation_type,
                description,
                batch_id,
                operazione.id_operazione  # Passa l'ID dell'operazione per aggiornare lo stato
            )
            
            # Mostra conferma all'utente
            QMessageBox.information(
                self,
                "Operazione registrata",
                f"L'operazione è stata registrata sulla blockchain con successo!\n\nHash transazione: {tx_hash}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Si è verificato un errore durante la registrazione dell'operazione sulla blockchain:\n{str(e)}"
            )
