# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout,
                             QPushButton, QMessageBox)

from model.richiesta_token_model import RichiestaTokenModel
from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.controller.company_controller import ControllerAzienda
from presentation.view import funzioni_utili
from session import Session


class VistaRiceviRichiesta(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.controller = ControllerAzienda()

        self.lista_prova : list[RichiestaTokenModel] = self.controller.get_richieste_ric_token()

        self.controllerAut = ControllerAutenticazione()

        self.token = self.controllerAut.get_user().token
        # Elementi di layout
        self.list_view = QListView()
        self.invia_button = QPushButton("Accetta")
        self.rifiuta_button = QPushButton("Rifiuta")

        self.setWindowIcon(QIcon("images\\logo_centro.png"))

        self.init_ui()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)  # Centra verticalmente

        label = QLabel(f"Token posseduti: {self.token}\n"
                       f"Richieste ricevute")

        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        funzioni_utili.insert_button(self.invia_button, button_layout)
        self.invia_button.clicked.connect(self.accetta_richiesta)

        funzioni_utili.insert_button(self.rifiuta_button, button_layout)
        self.rifiuta_button.clicked.connect(self.rifiuta_richiesta)

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def genera_lista(self):
        model = QStandardItemModel()
        for richiesta in self.lista_prova:
            item = QStandardItem(f"Quantità: {richiesta.quantita},\n"
                                 f"Mittente richiesta: {richiesta.mittente},\n"
                                 f"Destinatario richiesta: {richiesta.destinatario},\n"
                                 f"Stato: {richiesta.stato}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def accetta_richiesta(self):
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()
            richiesta = self.lista_prova[selected_item]

            try:

                if richiesta.stato != "In attesa":
                    raise ValueError("Richiesta già accettata o rifiutata.")

                self.controller.update_richiesta_token(richiesta , "Accettata")
                QMessageBox.information(self, "Supply Chain", f"{richiesta} accettata")
                # Aggiorna la lista dopo l'accettazione della richiesta
                self.lista_prova = self.controller.get_richieste_ric_token()
                self.genera_lista()
            except ValueError as e:
                QMessageBox.warning(self, "Errore", str(e))
                return
            
        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")

    def rifiuta_richiesta(self):
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()
            richiesta = self.lista_prova[selected_item]

            self.controller.update_richiesta_token(richiesta , "Rifiutata")

            QMessageBox.information(self, "Supply Chain", f"{richiesta} rifiutata")
            # Aggiorna la lista dopo il rifiuto della richiesta
            self.lista_prova = self.controller.get_richieste_ric_token()
            self.genera_lista()
        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")

