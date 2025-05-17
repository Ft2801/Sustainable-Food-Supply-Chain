from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from presentation.view import funzioni_utili
from presentation.view.vista_operazioni_azienda import OperazioniAziendaView


class VistaOperazioni(QMainWindow):
    """
    Main window for displaying and managing operations
    """
    closed = pyqtSignal()

    def __init__(self, controller=None, utente=None):
        super().__init__()
        self.controller = controller
        self.utente = utente
        
        self.setWindowTitle('Operazioni')
        self.setWindowIcon(QIcon("presentation/resources/logo_centro.png"))
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add the operations view
        operazioni_view = OperazioniAziendaView(self)
        main_layout.addWidget(operazioni_view)
        
        # Center the window on screen
        funzioni_utili.center(self)
    
    def closeEvent(self, event):
        """
        Override the close event to emit the closed signal
        """
        self.closed.emit()
        super().closeEvent(event)
