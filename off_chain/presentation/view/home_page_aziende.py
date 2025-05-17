from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox, QMenu, \
    QAction

from presentation.controller.company_controller import ControllerAzienda
from presentation.view import funzioni_utili
from presentation.view.istruzioni import Istruzioni
from presentation.view.vista_invia_richiesta import VistaInviaRichiesta
from presentation.view.vista_ricevi_richiesta import VistaRiceviRichiesta
from presentation.view.vista_riepilogo_operazioni import VistaRiepilogoOperazioni
from presentation.view.vista_stato_azienda import VistaStatoAzienda
from presentation.view.vista_azioni_compensative import VistaAzioniCompensative
from presentation.view.vista_operazioni import VistaOperazioni
from presentation.view.vista_soglie import VistaSoglie
from presentation.view.vista_sviluppatori import VistaSviluppatori


class HomePage(QMainWindow):
    def __init__(self, callback, utente):
        super().__init__()

        self.vista_riepilogo = None
        self.vista_ricevi_richieste = None
        self.vista_invia_richieste = None
        self.controller = ControllerAzienda()

        self.vista_soglie = None
        self.vista_sviluppatori = None
        self.stato = None
        self.vista_azioni = None
        self.vista_operazioni = None
        self.vista_istruzioni = None
        self.utente = utente

        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("background-color: rgb(240, 240, 240)")
        funzioni_utili.config_menubar(
            self, "File", QIcon("images\\exit.png"),
            "Logout", 'Ctrl+Q', self.menu_bar
        ).triggered.connect(self.logout)
        funzioni_utili.config_menubar(
            self, "Termini e condizioni d'uso", QIcon("images\\tcu.png"),
            "Leggi i termini e le condizioni d'uso", 'Ctrl+W', self.menu_bar
        ).triggered.connect(self.tcu)
        funzioni_utili.config_menubar(
            self, "FAQ", QIcon("images\\faq.png"),
            "Visualizza le domande più frequenti", 'Ctrl+E', self.menu_bar
        ).triggered.connect(self.faq)
        funzioni_utili.config_menubar(
            self, "Tutorial", QIcon("images\\tutorial.png"),
            "Visualizza tutorial", 'Ctrl+R', self.menu_bar
        ).triggered.connect(self.tutorial)

        self.setWindowIcon(QIcon("images\\logo_centro.png"))

        self.callback = callback

        # Elementi di layout
        self.logo = QLabel()
        self.welcome_label = QLabel(f"Ciao {self.utente['username']} 👋!\nBenvenuto in SupplyChain.\n"
                                    f"Prego selezionare un'opzione dal menu")
        self.button_operazioni = QPushButton('Operazioni')
        self.button_azioni_compensative = QPushButton('Azioni compensative')
        self.button_soglie = QPushButton('Soglie CO2')
        self.button_stato_azienda = QPushButton('Stato azienda')
        self.button_token = QPushButton('Gestione token')
        self.button_sviluppatori = QPushButton('Sviluppatori')

        # Inizializza il timer di inattività
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(funzioni_utili.timeout())
        self.inactivity_timer.timeout.connect(self.logout_per_inattivita)

        self.init_ui()
        self.start_inactivity_timer()
        self.installEventFilter(self)  # Intercetta eventi utente

    def start_inactivity_timer(self):
        """Avvia o resetta il timer di inattività."""
        self.inactivity_timer.start()

    def logout_per_inattivita(self):
        """Chiude la finestra se l'utente è inattivo per troppo tempo."""
        self.inactivity_timer.stop()
        reply = QMessageBox.warning(
            self,
            "Sessione scaduta",
            "Sei stato inattivo per troppo tempo. Verrai disconnesso.",
            QMessageBox.Ok
        )
        if reply == QMessageBox.Ok:
            self.close()
            self.callback()  # Torna alla schermata di login

    def eventFilter(self, obj, event):
        """Intercetta gli eventi dell'utente e resetta il timer."""
        if event.type() in (QEvent.MouseMove, QEvent.KeyPress):
            self.start_inactivity_timer()  # Reset del timer
        return super().eventFilter(obj, event)

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

        funzioni_utili.insert_button_in_grid(self.button_operazioni, button_layout, 1, 2)
        self.button_operazioni.clicked.connect(self.show_operazioni)

        funzioni_utili.insert_button_in_grid(self.button_azioni_compensative, button_layout, 1, 4)
        self.button_azioni_compensative.clicked.connect(self.show_azioni)

        funzioni_utili.insert_button_in_grid(self.button_soglie, button_layout, 3, 1)
        self.button_soglie.clicked.connect(self.show_soglie)

        funzioni_utili.insert_button_in_grid(self.button_stato_azienda, button_layout, 3, 5)
        self.button_stato_azienda.clicked.connect(self.show_stato)

        funzioni_utili.insert_button_in_grid(self.button_token, button_layout, 5, 2)
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

        funzioni_utili.insert_button_in_grid(self.button_sviluppatori, button_layout, 5, 4)
        self.button_sviluppatori.clicked.connect(self.show_sviluppatori)

        funzioni_utili.insert_logo(self.logo, button_layout, QPixmap("images\\logo_centro.png"))

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def logout(self):
        self.inactivity_timer.stop()
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

    def mostra(self):
        self.start_inactivity_timer()
        self.show()

    def tutorial(self):
        QMessageBox.information(
            self, 'SupplyChain', "Tutorial work in progress")

    def faq(self):
        QMessageBox.information(
            self, 'SupplyChain', "FAQ work in progress")

    def tcu(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_istruzioni = Istruzioni()
        self.vista_istruzioni.closed.connect(self.mostra)
        self.vista_istruzioni.show()

    def show_operazioni(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_operazioni = VistaOperazioni(
            self.controller, self.utente)
        self.vista_operazioni.closed.connect(self.mostra)
        self.vista_operazioni.show()

    def show_azioni(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_azioni = VistaAzioniCompensative(self.utente)
        self.vista_azioni.closed.connect(self.mostra)
        self.vista_azioni.show()

    def show_stato(self):
        self.inactivity_timer.stop()
        self.hide()
        self.stato = VistaStatoAzienda(self.aggiorna_profilo)
        self.stato.closed.connect(self.mostra)
        self.stato.show()

    def aggiorna_profilo(self, utente):
        self.utente = utente

    def show_sviluppatori(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_sviluppatori = VistaSviluppatori()
        self.vista_sviluppatori.closed.connect(self.mostra)
        self.vista_sviluppatori.show()

    def show_token(self):
        QMessageBox.information(
            self, 'SupplyChain', "Gestione token work in progress work in progress")

    def invia_richiesta(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_invia_richieste = VistaInviaRichiesta()
        self.vista_invia_richieste.closed.connect(self.mostra)
        self.vista_invia_richieste.show()

    def ricevi_richiesta(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_ricevi_richieste = VistaRiceviRichiesta()
        self.vista_ricevi_richieste.closed.connect(self.mostra)
        self.vista_ricevi_richieste.show()

    def riepilogo_richieste(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_riepilogo = VistaRiepilogoOperazioni()
        self.vista_riepilogo.closed.connect(self.mostra)
        self.vista_riepilogo.show()

    def show_soglie(self):
        self.inactivity_timer.stop()
        self.hide()
        self.vista_soglie = VistaSoglie()
        self.vista_soglie.closed.connect(self.mostra)
        self.vista_soglie.show()
