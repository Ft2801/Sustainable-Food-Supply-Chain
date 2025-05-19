# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from presentation.view import funzioni_utili
from presentation.view.vista_azioni_compensative_azienda import AzioniAziendaView


class VistaAzioniCompensative(QMainWindow):
    """
    Main window for displaying and managing compensatory actions
    """
    closed = pyqtSignal()

    def __init__(self, controller=None, utente=None):
        super().__init__()
        self.controller = controller
        self.utente = utente
        
        self.setWindowTitle('Azioni Compensative')
        self.setWindowIcon(QIcon("presentation/resources/logo_centro.png"))
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add the compensatory actions view
        azioni_view = AzioniAziendaView(self)
        main_layout.addWidget(azioni_view)
        
        # Center the window on screen
        funzioni_utili.center(self)
    
    def closeEvent(self, event):
        """
        Override the close event to emit the closed signal
        """
        self.closed.emit()
        super().closeEvent(event)
