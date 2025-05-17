# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout,
                             QPushButton)

from model.threshold_model import ThresholdModel
from presentation.view import funzioni_utili
from presentation.controller.company_controller import ControllerAzienda


class VistaSoglie(QMainWindow):
    """
    Window displaying CO2 thresholds
    """
    closed = pyqtSignal()
    def __init__(self, certificatore=None):
        super().__init__()

        self.controller = ControllerAzienda()

        self.lista : list[ThresholdModel] = self.controller.lista_soglie()

        # Elementi di layout
        self.list_view = QListView()
        self.modifica_button = QPushButton("Modifica soglia")

        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        self.init_ui()
        
    def closeEvent(self, event):
        """
        Override the close event to emit the closed signal
        """
        self.closed.emit()
        super().closeEvent(event)

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)  # Centra verticalmente

        label = QLabel("Lista soglie")

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
        for f in self.lista:
            item = QStandardItem(f"Operazione: {f.Tipo}\n"
                                 f"Prodotto: {f.Prodotto}\n"
                                 f"Soglia CO2: {f.Soglia_Massima}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)