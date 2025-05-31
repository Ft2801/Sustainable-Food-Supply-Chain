# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout
                        )

from model.richiesta_token_model import RichiestaTokenModel
from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.controller.company_controller import ControllerAzienda
from presentation.view import funzioni_utili
from presentation.controller.blockchain_controller import BlockchainController

class VistaRiepilogoOperazioni(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.controller = ControllerAzienda()

        self.lista_prova : list[RichiestaTokenModel]= self.controller.get_operazioni_token()
        self.controllerAut = ControllerAutenticazione()

        self.blockchain_controller = BlockchainController()

        # Elementi di layout
        self.list_view = QListView()

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

        label = QLabel(f"Token posseduti: {str(self.blockchain_controller.get_my_token_balance())}\n"
                       f"Riepilogo operazioni")

        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def genera_lista(self):
        model = QStandardItemModel()
        for richiesta in self.lista_prova:
            item = QStandardItem(f"Quantità: {richiesta.quantita},\n"
                                 f"Mittente: {richiesta.mittente},\n"
                                 f"Destinatario: {richiesta.destinatario},\n"
                                 f"Stato: {richiesta.stato}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

