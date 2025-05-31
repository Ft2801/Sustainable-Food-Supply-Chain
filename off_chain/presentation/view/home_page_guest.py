# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox


from presentation.view.vista_prodotti_guest import ProdottiFinitiView
from presentation.controller.guest_controller import ControllerGuest
from presentation.view import funzioni_utili
from presentation.view.vista_sviluppatori import VistaSviluppatori


class HomePageGuest(QMainWindow):
    def __init__(self, callback):
        super().__init__()

        #ControllerGuest = ControllerGuest
        self.controller = ControllerGuest()

        self.vista_prodotti = None
        self.vista_prodotti_certificati = None
        self.vista_aziende = None
        self.vista_sviluppatori = None

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
            "Visualizza tutorial", 'Ctrl+R', self.menu_bar
        ).triggered.connect(self.tutorial)

        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        self.callback = callback

        # Elementi di layout
        self.logo = QLabel()
        self.button_prodotti = QPushButton('Ricerca prodotti')
    

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

        welcome_label = QLabel("Benvenuto in SupplyChain.\nPrego selezionare un'opzione dal menu")
        funzioni_utili.insert_label(welcome_label, main_layout)

        button_layout = QGridLayout()
        button_layout.setSpacing(1)

        funzioni_utili.insert_button_in_grid(self.button_prodotti, button_layout, 2, 1)
        self.button_prodotti.clicked.connect(self.lista_prodotti_clicked)
        
        # Bottone per accedere alla vista sviluppatori
        self.button_sviluppatori = QPushButton('Sviluppatori')
        self.button_sviluppatori.clicked.connect(self.show_sviluppatori)
        funzioni_utili.insert_button_in_grid(self.button_sviluppatori, button_layout, 2, 4)


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
            self, 'SupplyChain', "Termini e condizioni d'uso work in progress")

    def lista_prodotti_clicked(self):
        self.vista_prodotti = ProdottiFinitiView()
        self.vista_prodotti.show()
        
    def show_sviluppatori(self):
        """Mostra la vista degli sviluppatori"""
        self.vista_sviluppatori = VistaSviluppatori()
        self.vista_sviluppatori.show()
