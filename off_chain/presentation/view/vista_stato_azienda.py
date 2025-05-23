# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QFormLayout, QLineEdit,
                             QHBoxLayout, QPushButton, QMessageBox)

from model.company_model import CompanyModel
from session import Session

from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.view import funzioni_utili
from presentation.view.vista_cambia_password import VistaCambiaPassword



class VistaStatoAzienda(QMainWindow):
    """
    Window displaying company status information
    """
    closed = pyqtSignal()
    def __init__(self, callback):
        super().__init__()

        self.callback = callback
        self.controller = ControllerAutenticazione()
        azienda : CompanyModel = self.controller.get_user()
        address = self.controller.blockchainconroller.get_adress(azienda.id_azienda)
        

        # Elementi di layout
        self.id_azienda_label = QLabel("ID")
        self.id_azienda_input = QLineEdit(str(azienda.id_azienda))

        self.nome_label = QLabel("Nome")
        self.nome_input = QLineEdit(str(azienda.nome))

        self.tipo_label = QLabel("Tipo")
        self.tipo_input = QLineEdit(str(azienda.tipo))

        self.addresslabel = QLabel("Indirizzo Blockchain")
        self.addressinput = QLineEdit(str(address))

        self.co2_consumata_totale_label = QLabel("CO2 consumata totale")
        self.co2_consumata_totale_input = QLineEdit(str(azienda.co2_consumata))

        self.co2_risparmiata_totale_label = QLabel("CO2 risparmiata totale")
        self.co2_risparmiata_totale_input = QLineEdit(str(azienda.co2_compensata)) 

        self.token_label = QLabel("Token accumulati")
        self.token_label_input = QLineEdit(str(azienda.token)) 

        self.cambia_password_button = QPushButton('Cambia password')
        self.cambia_password_button.clicked.connect(self.apri_cambia_password)

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

        welcome_label = QLabel('Informazioni azienda')
        funzioni_utili.insert_label(welcome_label, main_layout)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        form_container = QVBoxLayout()
        form_container.addLayout(form_layout)
        form_container.setContentsMargins(150, 0, 150, 0)

        self.id_azienda_input.setReadOnly(True)
        funzioni_utili.add_field_to_form(self.id_azienda_label, self.id_azienda_input, form_layout)

        self.nome_input.setReadOnly(True)
        # self.nome_input.setValidator(QRegExpValidator(QRegExp("[A-Za-z0-9 ]+")))  # Nome con lettere e numeri
        funzioni_utili.add_field_to_form(self.nome_label, self.nome_input, form_layout)

        self.tipo_input.setReadOnly(True)
        funzioni_utili.add_field_to_form(self.tipo_label, self.tipo_input, form_layout)


        if Session().current_user["role"] != "Certificatore":
            self.co2_consumata_totale_input.setReadOnly(True)
            funzioni_utili.add_field_to_form(self.co2_consumata_totale_label, self.co2_consumata_totale_input,
                                             form_layout)

            self.co2_risparmiata_totale_input.setReadOnly(True)
            funzioni_utili.add_field_to_form(self.co2_risparmiata_totale_label, self.co2_risparmiata_totale_input,
                                             form_layout)
            
            self.token_label_input.setReadOnly(True)
            funzioni_utili.add_field_to_form(self.token_label, self.token_label_input,
                                             form_layout)
            


        main_layout.addLayout(form_container)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        button_layout.addWidget(self.cambia_password_button)


        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def apri_cambia_password(self):
        self.vista_cambia_password = VistaCambiaPassword()
        self.vista_cambia_password.show()

    def aggiungi(self, id_azienda, nome, tipo, indirizzo):
        QMessageBox.information(self, "SupplyChain",
                                f"Dati azienda modificati correttamente:\n"
                                f"ID Azienda: {id_azienda}\n"
                                f"Nome: {nome}\n"
                                f"Tipo: {tipo}\n"
                                f"Indirizzo: {indirizzo}")
        self.callback((id_azienda, id_azienda, tipo, indirizzo, nome))
        self.close()
