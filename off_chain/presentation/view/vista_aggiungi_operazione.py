# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QDateEdit, QLineEdit, QComboBox, QDoubleSpinBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import pyqtSignal, Qt
from model.prodotto_finito_model import ProdottoLottoModel
from session import Session
from presentation.controller.company_controller import PERMESSI_OPERAZIONI, ControllerAzienda
from PyQt5.QtWidgets import  QMessageBox
from model.product_standard_model import ProductStandardModel


class AggiungiOperazioneView(QDialog):
    operazione_aggiunta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()
        self.role_azienda : str = Session().current_user["role"]
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Aggiungi Operazione")

        layout = QVBoxLayout()

        

        layout.addWidget(QLabel("Tipo operazione:"))
        self.input_tipo = QComboBox()
        permessi = PERMESSI_OPERAZIONI.get(self.role_azienda, [])
        self.input_tipo.addItems(permessi)
        layout.addWidget(self.input_tipo)


        self.input_testo = QLineEdit()
        self.input_testo.setMaxLength(25)


        self.input_ricerca_prodotto = QLineEdit()
        self.lista_prodotti = QListWidget()
        self.lista_prodotti.setSelectionMode(QListWidget.NoSelection)  

        if self.role_azienda == "Agricola" :
        
            layout.addWidget(QLabel("Seleziona il tipo di prodotto:"))

            self.input_combo_prodotto = QComboBox()
            self.prodotti_agricoli : list[ProductStandardModel] = self.controller.get_prodotti_standard()
            for prodotto in self.prodotti_agricoli:
                self.input_combo_prodotto.addItem(prodotto.Nome_prodotto, prodotto.Id_prodotto)  # nome visibile, ID come userData
            layout.addWidget(self.input_combo_prodotto)

            # Campo descrizione rimosso


            self.input_quantita = QDoubleSpinBox()
            self.input_quantita.setMinimum(0.0)
            self.input_quantita.setMaximum(10000.0)
            self.input_quantita.setDecimals(0)
            self.input_quantita.setSingleStep(1)
            layout.addWidget(QLabel("Inserisci quantità prodotta:"))
            layout.addWidget(self.input_quantita)







        

        if  self.role_azienda == "Trasportatore" or self.role_azienda == "Rivenditore":

            # Se il ruolo è Trasformatore, Trasportatore o Rivenditore, mostra la lista dei prodotti

            layout.addWidget(QLabel("Seleziona il prodotto:"))

            if self.role_azienda in ["Rivenditore"]:  
                self.abilita_selezione_singola()


            self.input_ricerca_prodotto.setPlaceholderText("Cerca per nome o ID...")
            layout.addWidget(self.input_ricerca_prodotto)

            
            layout.addWidget(self.lista_prodotti)

            self.prodotti_completi: list[ProdottoLottoModel] = self.controller.get_prodotti_to_composizione()

            self.popola_lista_prodotti(self.prodotti_completi)

            # Collegamento del filtro
            self.input_ricerca_prodotto.textChanged.connect(self.filtra_lista_prodotti)


            self.input_quantita = QDoubleSpinBox()
            self.input_quantita.setMinimum(0.0)            
            self.input_quantita.setMaximum(10000.0)       
            self.input_quantita.setDecimals(0)          
            self.input_quantita.setSingleStep(1)                    
            layout.addWidget(QLabel("Inserisci quantità prodotto:"))
            layout.addWidget(self.input_quantita)



        layout.addWidget(QLabel("Data:"))
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        layout.addWidget(self.input_data)

        

        self.input_valore = QDoubleSpinBox()
        self.input_valore.setMinimum(0.0)            
        self.input_valore.setMaximum(9999.99)       
        self.input_valore.setDecimals(0)          
        self.input_valore.setSingleStep(1)                    
        layout.addWidget(QLabel("Inserisci un valore CO2:"))
        layout.addWidget(self.input_valore)


        self.btn_salva = QPushButton("Salva operazione")
        self.btn_salva.clicked.connect(self.salva_operazione)
        layout.addWidget(self.btn_salva)

        self.setLayout(layout)

        self.resize(400, 300)
        self.raise_()
        self.activateWindow()


    def salva_operazione(self):
        try:
            tipo = self.input_tipo.currentText()
            data = self.input_data.date().toPyDate()
            co2 = self.input_valore.value()
            quantita = self.input_quantita.value()


            # Controlli di validità base
            if not tipo:
                QMessageBox.warning(self, "Errore", "Tipo operazione mancante.")
                return

            if co2 <= 0:
                QMessageBox.warning(self, "Errore", "Inserisci un valore di CO2 positivo.")
                return

             # Raccolta dei dati specifici in base al ruolo
            if self.role_azienda == "Agricola":
                nome_nuovo_prodotto = self.input_combo_prodotto.currentText()
                if not nome_nuovo_prodotto:
                    QMessageBox.warning(self, "Errore", "Seleziona una tipologia di prodotto.")
                    return
                
                id_prodotto_base = self.input_combo_prodotto.currentData()
                # Descrizione rimossa
                descrizione = ""  # Valore vuoto per la descrizione

                if not id_prodotto_base:
                    QMessageBox.warning(self, "Errore", "Seleziona una tipologia di prodotto.")
                    return

                self.controller.salva_operazione_agricola(
                    tipo=tipo,
                    data=data,
                    co2=co2,
                    id_tipo_prodotto=id_prodotto_base,
                    descrizione=descrizione,  # Passiamo una stringa vuota
                    quantita=quantita
                )

            

            elif self.role_azienda == "Rivenditore":
                prodotti_selezionati = self.get_prodotti_selezionati()

                if not prodotti_selezionati:
                    QMessageBox.warning(self, "Errore", "Seleziona un prodotto.")
                    return
                if len(prodotti_selezionati) > 1:
                    QMessageBox.warning(self, "Errore", "Puoi selezionare solo un prodotto.")
                    return

                prodotto = prodotti_selezionati[0]

                if quantita <= 0:
                    QMessageBox.warning(self, "Errore", "Inserisci una quantità positiva.")
                    return

                if quantita > prodotto.quantita:
                    QMessageBox.warning(self, "Errore", f"La quantità inserita ({quantita}) supera quella disponibile ({prodotto.quantita}).")
                    return

                id_prodotto = prodotto.id_prodotto
                numero_lotto = prodotto.id_lotto  # Assicurati che questo attributo esista

                self.controller.salva_operazione_distributore(
                    data=data,
                    co2=co2,
                    id_prodotto=id_prodotto,
                    id_lotto_input=numero_lotto,
                    quantita=quantita
                )



            else:
                QMessageBox.critical(self, "Errore", f"Ruolo azienda non gestito: {self.role_azienda}")
                return

            # Successo
            self.operazione_aggiunta.emit()
            self.accept()

        except PermissionError as e:
                QMessageBox.critical(self, "Errore di permesso", str(e))
        except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'aggiunta: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")


            


            



    def popola_lista_prodotti(self, prodotti: list[ProdottoLottoModel]):
        self.lista_prodotti.clear()
        for prodotto in prodotti:
            item = QListWidgetItem(f"{prodotto.nome} (ID_lotto: {prodotto.id_prodotto}) Quantità{prodotto.quantita}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, prodotto)
            self.lista_prodotti.addItem(item)

    def filtra_lista_prodotti(self, testo: str):
        testo = testo.lower().strip()
        prodotti_filtrati = [
            p for p in self.prodotti_completi
            if testo in p.nome.lower() or testo in str(p.id_lotto)
        ]
        self.popola_lista_prodotti(prodotti_filtrati)



    def abilita_selezione_singola(self):
        for i in range(self.lista_prodotti.count()):
            item = self.lista_prodotti.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        self.lista_prodotti.itemChanged.connect(self.gestisci_selezione_singola)

    def gestisci_selezione_singola(self, item_selezionato: QListWidgetItem):
        if item_selezionato.checkState() == Qt.Checked:
            for i in range(self.lista_prodotti.count()):
                item = self.lista_prodotti.item(i)
                if item != item_selezionato and item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)

    def get_prodotti_selezionati(self) -> list[ProdottoLottoModel]:
        prodotti = []
        for i in range(self.lista_prodotti.count()):
            item = self.lista_prodotti.item(i)
            if item.checkState() == Qt.Checked:
                prodotto = item.data(Qt.UserRole)
                prodotti.append(prodotto)
        return prodotti



