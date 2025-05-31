# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout,
    QPushButton, QMessageBox, QMenu, QAction
)

from presentation.view.vista_contratti_deploy import OperazioniCompanyView
from presentation.view.vista_richieste import VisualizzaRichiesteView
from presentation.view.vista_magazzino import VisualizzaMagazzinoView
from presentation.controller.company_controller import ControllerAzienda
from presentation.view import funzioni_utili
from presentation.view.vista_stato_azienda import VistaStatoAzienda
from presentation.view.vista_operazioni_azienda import OperazioniAziendaView
from presentation.view.vista_azioni_compensative_azienda import AzioniAziendaView
from presentation.view.vista_invia_richiesta import VistaInviaRichiesta
from presentation.view.vista_ricevi_richiesta import VistaRiceviRichiesta
from presentation.view.vista_riepilogo_operazioni import VistaRiepilogoOperazioni
from session import Session
from presentation.view.vista_soglie_azienda import SoglieAziendaView
from persistence.repository_impl import db_default_string
from presentation.view.vista_sviluppatori import VistaSviluppatori


class HomePage(QMainWindow):
    def __init__(self, callback, utente):
        super().__init__()

        self.controller = ControllerAzienda()
        self.callback = callback
        self.utente = utente

        self.init_views()
        self.init_ui()
        self.setup_menu()

    def init_views(self):
        self.vista_soglie = None
        self.vista_richieste = None
        self.vista_stato = None
        self.vista_azioni = None
        self.vista_operazioni = None
        self.vista_magazzino = None
        self.vista_riepilogo = None
        self.vista_ricevi_richieste = None
        self.vista_invia_richieste = None
        self.vista_sviluppatori = None
        self.vista_catena_operazioni = None

    def setup_menu(self):
        menu = self.menuBar()
        menu.setStyleSheet("background-color: rgb(240, 240, 240)")

        funzioni_utili.config_menubar(
            self, "File", QIcon("presentation/resources/exit.png"),
            "Logout", 'Ctrl+Q', menu).triggered.connect(self.logout)

        funzioni_utili.config_menubar(
            self, "Termini e condizioni d'uso", QIcon("presentation/resources/tcu.png"),
            "Leggi i termini e condizioni d'uso", 'Ctrl+W', menu).triggered.connect(self.tcu)

        funzioni_utili.config_menubar(
            self, "FAQ", QIcon("presentation/resources/faq.png"),
            "Visualizza le domande frequenti", 'Ctrl+E', menu).triggered.connect(self.faq)

        funzioni_utili.config_menubar(
            self, "Tutorial", QIcon("presentation/resources/tutorial.png"),
            "Visualizza tutorial", 'Ctrl+R', menu).triggered.connect(self.tutorial)

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)
        self.setWindowIcon(QIcon("presentation/resources/logo_centro.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignCenter)

        welcome_msg = f"Ciao {Session().current_user['username']} !\nBenvenuto in SupplyChain.\nPrego selezionare un'opzione dal menu"
        self.welcome_label = QLabel(welcome_msg)
        funzioni_utili.insert_label(self.welcome_label, main_layout)

        self.logo = QLabel()
        button_layout = QGridLayout()
        button_layout.setSpacing(20)

        self.setup_buttons(button_layout)
        funzioni_utili.insert_logo(self.logo, button_layout, QPixmap("presentation/resources/logo_centro.png"))

        main_layout.addLayout(button_layout)
        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def setup_buttons(self, layout):
        if Session().current_user["role"] != db_default_string.TIPO_AZIENDA_CERTIFICATORE:
            self.button_operazioni = QPushButton('Operazioni')
            self.button_operazioni.clicked.connect(self.show_operazioni)
            funzioni_utili.insert_button_in_grid(self.button_operazioni, layout, 1, 2)

        self.button_azioni_compensative = QPushButton('Azioni compensative')
        self.button_azioni_compensative.clicked.connect(self.show_azioni)
        funzioni_utili.insert_button_in_grid(self.button_azioni_compensative, layout, 1, 3)

        self.button_magazzino = QPushButton('Magazzino')
        self.button_magazzino.clicked.connect(self.show_magazzino)
        funzioni_utili.insert_button_in_grid(self.button_magazzino, layout, 1, 6)

        self.button_soglie = QPushButton('Soglie CO2')
        self.button_soglie.clicked.connect(self.show_soglie)
        funzioni_utili.insert_button_in_grid(self.button_soglie, layout, 3, 2)

        self.button_stato_azienda = QPushButton('Stato azienda')
        self.button_stato_azienda.clicked.connect(self.show_stato)
        funzioni_utili.insert_button_in_grid(self.button_stato_azienda, layout, 3, 6)

        self.button_token = QPushButton('Gestione token')
        self.button_token.clicked.connect(self.show_token)
        funzioni_utili.insert_button_in_grid(self.button_token, layout, 5, 2)

        self.button_catena_operazioni = QPushButton('Catena Operazioni')
        self.button_catena_operazioni.clicked.connect(self.show_catena_operazioni)
        funzioni_utili.insert_button_in_grid(self.button_catena_operazioni, layout, 6, 6)

        # Aggiunta Domenico
        menu_token = QMenu(self)

        azione_invia = QAction("Richiedi token", self)
        azione_ricevi = QAction("Invia token", self)
        azione_riepilogo = QAction("Riepilogo operazioni", self)

        azione_invia.triggered.connect(self.invia_richiesta)
        azione_ricevi.triggered.connect(self.ricevi_richiesta)
        azione_riepilogo.triggered.connect(self.riepilogo_richieste)

        menu_token.addAction(azione_invia)
        menu_token.addAction(azione_ricevi)
        menu_token.addAction(azione_riepilogo)

        self.button_token.setMenu(menu_token)
        # Fin qui

        self.button_richieste = QPushButton('Richieste')
        self.button_richieste.clicked.connect(self.show_richieste)
        funzioni_utili.insert_button_in_grid(self.button_richieste, layout, 5, 3)
        
        # Bottone per accedere alla vista sviluppatori
        self.button_sviluppatori = QPushButton('Sviluppatori')
        self.button_sviluppatori.clicked.connect(self.show_sviluppatori)
        funzioni_utili.insert_button_in_grid(self.button_sviluppatori, layout, 5, 6)

    def logout(self):

        reply = QMessageBox.question(
            self, "Conferma logout", "Sei sicuro di voler effettuare il logout?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No

        )

        if reply == QMessageBox.Yes:
            self.close()
            self.callback()

    def tutorial(self):
        QMessageBox.information(self, 'SupplyChain', "Tutorial in lavorazione")

    def faq(self):
        QMessageBox.information(self, 'SupplyChain', "FAQ in lavorazione")

    def tcu(self):
        QMessageBox.information(self, 'SupplyChain', "Termini e condizioni d'uso in lavorazione")

    def show_operazioni(self):
        self.vista_operazioni = OperazioniAziendaView()
        self.vista_operazioni.setWindowModality(Qt.ApplicationModal)

        self.vista_operazioni.show()

    def show_azioni(self):
        self.vista_azioni = AzioniAziendaView()

        self.vista_azioni.show()

    def show_magazzino(self):
        self.vista_magazzino = VisualizzaMagazzinoView()
        self.vista_magazzino.show()

    def show_stato(self):
        self.vista_stato = VistaStatoAzienda(self.aggiorna_profilo)
        self.vista_stato.show()

    def show_richieste(self):
        self.vista_richieste = VisualizzaRichiesteView()
        self.vista_richieste.show()

    def show_soglie(self):
        self.vista_soglie = SoglieAziendaView()
        self.vista_soglie.show()

    def show_token(self):
        QMessageBox.information(self, 'SupplyChain', "Gestione token in lavorazione")

    # Aggiunta Domenico
    def invia_richiesta(self):
        self.hide()
        self.vista_invia_richieste = VistaInviaRichiesta()
        self.vista_invia_richieste.closed.connect(self.mostra)
        self.vista_invia_richieste.show()

    def ricevi_richiesta(self):
        self.hide()
        self.vista_ricevi_richieste = VistaRiceviRichiesta()
        self.vista_ricevi_richieste.closed.connect(self.mostra)
        self.vista_ricevi_richieste.show()

    def riepilogo_richieste(self):
        self.hide()
        self.vista_riepilogo = VistaRiepilogoOperazioni()
        self.vista_riepilogo.closed.connect(self.mostra)
        self.vista_riepilogo.show()
    # Fin qui

    def aggiorna_profilo(self, utente):
        self.utente = utente
        self.welcome_label.setText(
            f"Ciao {Session().current_user['username']} !\nBenvenuto in SupplyChain.\nPrego selezionare un'opzione dal menu"
        )
        
    def mostra(self):
        """Mostra la finestra principale"""
        self.show()
        
    def show_sviluppatori(self):
        """Mostra la vista degli sviluppatori"""
        self.vista_sviluppatori = VistaSviluppatori()
        self.vista_sviluppatori.closed.connect(self.mostra)
        self.vista_sviluppatori.show()
        
    def show_catena_operazioni(self):
        """Mostra la vista della catena di operazioni sulla blockchain"""
        self.vista_catena_operazioni = OperazioniCompanyView()
        self.vista_catena_operazioni.show()