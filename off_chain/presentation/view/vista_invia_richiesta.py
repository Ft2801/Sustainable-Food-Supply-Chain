# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout,
                             QPushButton, QMessageBox, QDialog, QDialogButtonBox, QComboBox)

from presentation.view import funzioni_utili


class VistaInviaRichiesta(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.lista_prova = [
            # Quantità, mittente, destinatario, stato
            (100, "Azienda 2", "Azienda 1", "in attesa"),
            (200, "Azienda 2", "Azienda 3", "in attesa"),
            (150, "Azienda 2", "Azienda 4", "in attesa"),
            (175, "Azienda 2", "Azienda 5", "in attesa")
        ]

        self.token = 500

        # Elementi di layout
        self.list_view = QListView()
        self.invia_button = QPushButton("Invia nuova richiesta")

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
                       f"Richieste inviate")

        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        funzioni_utili.insert_button(self.invia_button, button_layout)
        self.invia_button.clicked.connect(self.invia_richiesta)

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def genera_lista(self):
        model = QStandardItemModel()
        for f in self.lista_prova:
            item = QStandardItem(f"Quantità: {f[0]},\n"
                                 f"Mittente richiesta: {f[1]},\n"
                                 f"Destinatario richiesta: {f[2]},\n"
                                 f"Stato: {f[3]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def invia_richiesta(self):
        # Crea un QDialog personalizzato
        dialog = QDialog(self)
        dialog.setWindowTitle("SupplyChain")

        layout = QVBoxLayout(dialog)

        label = QLabel("Seleziona la quantità di token e l'azienda")
        layout.addWidget(label)

        # Crea una QComboBox e aggiungi le opzioni
        combo = QComboBox(dialog)
        options = [str(i) for i in range(1000)]
        combo.addItems(options)
        layout.addWidget(combo)

        combo_aziende = QComboBox(dialog)
        aziende = ["Azienda 1", "Azienda 3", "Azienda 4", "Azienda 5"]
        combo_aziende.addItems(aziende)
        layout.addWidget(combo_aziende)

        # Aggiungi i pulsanti "Ok" e "Cancel"
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(buttons)

        # Definisci cosa succede quando l'utente clicca su "Ok"
        def on_accept():
            selected_option = combo.currentText()
            selected_azienda = combo_aziende.currentText()
            if selected_option.strip() == "":
                QMessageBox.warning(dialog, 'Errore', 'Devi selezionare qualcosa!')
            else:
                self.lista_prova.append((int(selected_option), "Azienda 2", selected_azienda, "in attesa"))
                self.genera_lista()
                dialog.accept()
                QMessageBox.information(self, "Supply Chain",
                                        "Richiesta inviata correttamente")

        # Collega i pulsanti alle funzioni
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        # Mostra il dialogo
        dialog.exec_()

