# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout)

from presentation.view import funzioni_utili


class VistaSviluppatori(QMainWindow):
    """
    Window displaying information about the developers
    """
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Sviluppatori')
        self.setWindowIcon(QIcon("presentation/resources/logo_centro.png"))
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Sviluppatori")
        title_label.setFont(QFont("Times Roman", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Developers information
        developers_layout = QVBoxLayout()
        
        # Add developer information (placeholder - replace with actual developer info)
        self._add_developer(developers_layout, "Developer 1", "Luca Marcianesi", "S1127075@studenti.univpm.it")
        self._add_developer(developers_layout, "Developer 2", "Fabio Tempera", "S1125574@studenti.univpm.it")
        self._add_developer(developers_layout, "Developer 3", "Gianluca Baldelli", "S1121772@studenti.univpm.it")
        self._add_developer(developers_layout, "Developer 4", "Domenico La Porta", "S1125535@studenti.univpm.it")
        self._add_developer(developers_layout, "Developer 5", "Catalina Martha Quispe Ipurre", "S1121594@studenti.univpm.it")
        
        main_layout.addLayout(developers_layout)
        
        # Add logo at the bottom
        logo_label = QLabel()
        logo_pixmap = QPixmap("presentation/resources/logo_trasparente.png")
        logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # Center the window on screen
        funzioni_utili.center(self)
    
    def _add_developer(self, layout, name, role, contact):
        """Helper method to add a developer's information to the layout"""
        dev_layout = QVBoxLayout()
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Times Roman", 14, QFont.Bold))
        
        role_label = QLabel(role)
        contact_label = QLabel(contact)
        
        dev_layout.addWidget(name_label)
        dev_layout.addWidget(role_label)
        dev_layout.addWidget(contact_label)
        
        layout.addLayout(dev_layout)
        layout.addSpacing(20)
    
    def closeEvent(self, event):
        """
        Override the close event to emit the closed signal
        """
        self.closed.emit()
        super().closeEvent(event)
