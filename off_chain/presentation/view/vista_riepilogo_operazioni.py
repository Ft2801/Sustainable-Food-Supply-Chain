# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout,
                             QPushButton, QMessageBox, QDialog, QDialogButtonBox, QComboBox)

from presentation.view import funzioni_utili


class VistaRiepilogoOperazioni(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.lista_prova = [
            # Quantità, mittente, destinatario, stato
            (100, "Azienda 2", "Azienda 1", "accettata"),
            (200, "Azienda 2", "Azienda 3", "rifiutata"),
            (150, "Azienda 2", "Azienda 4", "accettata"),
            (175, "Azienda 2", "Azienda 5", "accettata"),
            (100, "Azienda 1", "Azienda 2", "rifiutata"),
            (200, "Azienda 3", "Azienda 2", "rifiutata"),
            (150, "Azienda 4", "Azienda 2", "accettata"),
            (175, "Azienda 5", "Azienda 2", "rifiutata")
        ]

        self.token = 500

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

        label = QLabel(f"Token posseduti: {500}\n"
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
        for f in self.lista_prova:
            item = QStandardItem(f"Quantità: {f[0]},\n"
                                 f"Mittente: {f[1]},\n"
                                 f"Destinatario: {f[2]},\n"
                                 f"Stato: {f[3]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

