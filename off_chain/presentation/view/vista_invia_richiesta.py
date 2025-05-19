# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout,
                             QPushButton, QMessageBox, QDialog, QDialogButtonBox, QComboBox)

from model.richiesta_token_model import RichiestaTokenModel
from model.company_model import CompanyModel
from presentation.controller.company_controller import ControllerAzienda
from session import Session
from presentation.view import funzioni_utili


class VistaInviaRichiesta(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.controller = ControllerAzienda()

        self.lista_prova : list[RichiestaTokenModel]= self.controller.get_richiesta_inv_token()
        self.lista_aziende : list[CompanyModel] = self.controller.get_aziende()

        self.token  = Session()._current_user.token

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

        for richiesta in self.lista_prova:
            if isinstance(richiesta, RichiestaTokenModel):
                
                item = QStandardItem(f"Quantità: {richiesta.quantita},\n"
                                    f"Mittente richiesta: {richiesta.mittente},\n"
                                    f"Destinatario richiesta: {richiesta.destinatario},\n"
                                    f"Stato: {richiesta.stato}")
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
        for azienda in self.lista_aziende:
            combo_aziende.addItem(azienda.nome, azienda.id_azienda)
        layout.addWidget(combo_aziende)

        # Aggiungi i pulsanti "Ok" e "Cancel"
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(buttons)

        # Definisci cosa succede quando l'utente clicca su "Ok"
        def on_accept():
            selected_option = combo.currentText()
            id_azienda_dest = combo_aziende .currentData()
            nome_azienda_dest = combo_aziende.currentText()
            if selected_option.strip() == "":
                QMessageBox.warning(dialog, 'Errore', 'Devi selezionare qualcosa!')
            else:
                dialog.accept()
                try:
                    self.controller.send_richiesta_token(id_azienda_dest, int(selected_option))
                except ValueError:
                    QMessageBox.warning(self, "Errore", "Devi selezionare un numero valido.")
                    return
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Errore durante l'invio della richiesta: {str(e)}")
                    return
                
                QMessageBox.information(self, "Supply Chain", "Richiesta inviata correttamente")

        # Collega i pulsanti alle funzioni
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        # Mostra il dialogo
        dialog.exec_()

