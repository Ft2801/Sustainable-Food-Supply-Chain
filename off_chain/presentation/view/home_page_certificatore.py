# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox

from presentation.view.vista_lotti_certificatore import VistaRicercaLotti
from session import Session
from presentation.controller.certification_controller import ControllerCertificatore
from presentation.view import funzioni_utili
from presentation.view.vista_stato_azienda import VistaStatoAzienda
from presentation.view.vista_soglie import VistaSoglie


class HomePageCertificatore(QMainWindow):
    def __init__(self, callback):
        super().__init__()

        self.controller = ControllerCertificatore()

        self.vista_soglie = None
        self.vista_azienda = None
        self.vista_certificazioni = None

        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("background-color: rgb(240, 240, 240)")
        funzioni_utili.config_menubar(
            self, "File", QIcon("presentation\\resources\\exit.png"),
            "Logout", 'Ctrl+Q', self.menu_bar
        ).triggered.connect(self.logout)
        funzioni_utili.config_menubar(
            self, "Termini e condizioni d'uso", QIcon("presentation\\resources\\tcu.png"),
            "Leggi i termini e le condizioni d'uso", 'Ctrl+W', self.menu_bar
        ).triggered.connect(self.tcu)
        funzioni_utili.config_menubar(
            self, "FAQ", QIcon("presentation\\resources\\faq.png"),
            "Visualizza le domande più frequenti", 'Ctrl+E', self.menu_bar
        ).triggered.connect(self.faq)
        funzioni_utili.config_menubar(
            self, "Tutorial", QIcon("presentation\\resources\\tutorial.png"),
            "Visualizza tutorial", 'Ctrl+E', self.menu_bar
        ).triggered.connect(self.tutorial)

        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        self.callback = callback

        # Elementi di layout
        self.logo = QLabel()
        self.welcome_label = QLabel(f"Ciao {Session().current_user['username']} 👋!\nBenvenuto in SupplyChain.\n"
                                    f"Prego selezionare un'opzione dal menu")
        self.button_certificazione = QPushButton('Certificazioni')
        self.button_aziende = QPushButton('Stato azienda')
        self.button_soglie = QPushButton('Soglie')
       

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignCenter)

        funzioni_utili.insert_label(self.welcome_label, main_layout)

        button_layout = QGridLayout()
        button_layout.setSpacing(1)

        funzioni_utili.insert_button_in_grid(self.button_certificazione, button_layout, 1, 2)
        self.button_certificazione.clicked.connect(self.show_certificazioni)

        funzioni_utili.insert_button_in_grid(self.button_aziende, button_layout, 1, 4)
        self.button_aziende.clicked.connect(self.show_azienda)

        funzioni_utili.insert_button_in_grid(self.button_soglie, button_layout, 5, 2)
        self.button_soglie.clicked.connect(self.show_soglie)

        funzioni_utili.insert_logo(self.logo, button_layout, QPixmap("presentation\\resources\\logo_centro.png"))

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def logout(self):
        # Mostra una finestra di conferma
        reply = QMessageBox.question(
            self,
            "Conferma logout",
            "Sei sicuro di voler effettuare il logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Procede solo se l'utente clicca "Yes"
        if reply == QMessageBox.Yes:
            Session().end_session()
            self.close()
            self.callback()

    def tutorial(self):
        QMessageBox.information(
            self, 'SupplyChain', 'Tutorial work in progress')

    def faq(self):
        QMessageBox.information(
            self, 'SupplyChain', "FAQ work in progress")

    def tcu(self):
        QMessageBox.information(
            self, 'SupplyChain', 'TCU work in progress')

    def show_certificazioni(self):
        self.vista_certificazioni = VistaRicercaLotti()
        self.vista_certificazioni.show()

    

    def aggiorna_profilo(self):
        self.welcome_label.setText(
            f"Ciao {Session().current_user['username']} 👋!\nBenvenuto in SupplyChain.\n"
            f"Prego selezionare un'opzione dal menu"
        )

    def show_soglie(self):
        self.vista_soglie = VistaSoglie(True)
        self.vista_soglie.show()

    def show_azienda(self):
        self.vista_azienda = VistaStatoAzienda(self.aggiorna_profilo)
        self.vista_azienda.show()
