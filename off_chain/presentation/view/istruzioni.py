from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QTextEdit

class Istruzioni(QWidget):
    """
    Class for displaying terms and conditions or instructions to the user
    """
    closed = pyqtSignal()  # Signal emitted when the window is closed

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Termini e Condizioni d'Uso")
        self.setWindowIcon(QIcon("presentation/resources/logo_centro.png"))
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Termini e Condizioni d'Uso")
        title_label.setFont(QFont("Times Roman", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Terms and conditions text
        terms_text = QTextEdit()
        terms_text.setReadOnly(True)
        terms_text.setHtml(self._get_terms_content())
        content_layout.addWidget(terms_text)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Close button
        close_button = QPushButton("Ho letto e accetto")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
    
    def _get_terms_content(self):
        """
        Returns the HTML content for the terms and conditions
        """
        return """
        <h2>Termini e Condizioni d'Uso della Piattaforma SupplyChain</h2>
        
        <h3>1. Introduzione</h3>
        <p>Benvenuto nella piattaforma SupplyChain per la gestione sostenibile della filiera alimentare. 
        Questi termini e condizioni regolano l'utilizzo della piattaforma e dei servizi correlati.</p>
        
        <h3>2. Definizioni</h3>
        <p><strong>Piattaforma:</strong> Si riferisce all'applicazione SupplyChain, inclusi tutti i suoi componenti software.</p>
        <p><strong>Utente:</strong> Qualsiasi entità o individuo che utilizza la piattaforma.</p>
        <p><strong>Dati:</strong> Informazioni inserite, generate o elaborate all'interno della piattaforma.</p>
        
        <h3>3. Registrazione e Account</h3>
        <p>Per utilizzare la piattaforma, è necessario registrarsi e creare un account. L'utente è responsabile della sicurezza delle proprie credenziali di accesso.</p>
        
        <h3>4. Utilizzo della Piattaforma</h3>
        <p>La piattaforma deve essere utilizzata esclusivamente per scopi legittimi legati alla gestione della filiera alimentare sostenibile.</p>
        
        <h3>5. Blockchain e Smart Contracts</h3>
        <p>La piattaforma utilizza tecnologia blockchain e smart contracts per garantire la tracciabilità e la trasparenza delle operazioni.</p>
        
        <h3>6. Responsabilità</h3>
        <p>L'utente è responsabile dell'accuratezza dei dati inseriti nella piattaforma. La piattaforma non è responsabile per eventuali perdite o danni derivanti dall'uso improprio.</p>
        
        <h3>7. Privacy e Protezione dei Dati</h3>
        <p>La piattaforma raccoglie e processa dati in conformità con le normative sulla privacy applicabili.</p>
        
        <h3>8. Modifiche ai Termini</h3>
        <p>Questi termini possono essere modificati periodicamente. Gli utenti saranno informati di eventuali modifiche significative.</p>
        
        <h3>9. Legge Applicabile</h3>
        <p>Questi termini sono regolati dalle leggi italiane.</p>
        """
    
    def closeEvent(self, event):
        """
        Override the close event to emit the closed signal
        """
        self.closed.emit()
        super().closeEvent(event)
