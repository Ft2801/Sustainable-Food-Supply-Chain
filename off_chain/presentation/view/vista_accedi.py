# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QMainWindow, QAction, QCheckBox, QStackedWidget, \
    QComboBox, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from model.credential_model import UserModel
from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.view import funzioni_utili
from presentation.view.home_page_aziende import HomePage
from presentation.view.home_page_certificatore import HomePageCertificatore
from presentation.view.home_page_guest import HomePageGuest
from session import Session
import sys
import subprocess

''''
Class for authentication view main
'''


class VistaAccedi(QMainWindow):
    """
    Constructor "__init__" of the class VistaAccedi
    """

    def __init__(self):
        super().__init__()

        self.controller = ControllerAutenticazione()  # instance of the class ControllerAutenticazione
        self.home_certificatore = None
        self.home_page = None
        self.home_guest = None
        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        # Elementi di layout
        self.login_label = QLabel("Login")
        self.section_switcher = QCheckBox()
        self.register_label = QLabel("Registrati")
        self.stacked_widget = QStackedWidget()

        self.username_label = QLabel('Nome Azienda:')
        self.username_input = QLineEdit()
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.otp_input = QLineEdit()
        self.login_button = QPushButton('Accedi')
        self.guest_button = QPushButton('Entra come guest')
        self.logo = QLabel()

        self.username_label_ = QLabel('Nome Azienda:')
        self.username_input_ = QLineEdit()
        self.tipo_label = QLabel('Tipo Azienda:')
        self.tipo_input = QComboBox()
        self.indirizzo_label = QLabel('Indirizzo:')
        self.indirizzo_input = QLineEdit()
        self.password_label_ = QLabel('Password:')
        self.password_input_ = QLineEdit()
        self.conferma_password_label = QLabel('Conferma Password:')
        self.conferma_password_input = QLineEdit()
        self.tcu_cb = QCheckBox("Ho letto e accetto i termini e le condizioni d'uso")
        self.tcu = QLabel("Visualizza i termini e le condizioni d'uso")
        self.password = [
            self.password_input, self.password_input_, self.conferma_password_input]
        self.icons_action = []
        self.register_button = QPushButton('Registrati')

        self.password_visibile = False

        self.init_ui_()

    ''''
    Configure the UI main
    '''

    def init_ui_(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setAlignment(Qt.AlignCenter)  # Centra verticalmente

        # Add section switcher
        switcher_layout = QHBoxLayout()
        switcher_layout.setAlignment(Qt.AlignCenter)

        self.login_label.setFont(QFont("Times Roman", 11, QFont.Bold))
        self.login_label.setStyleSheet("color: green")

        self.section_switcher.setFixedSize(60, 30)
        self.section_switcher.setStyleSheet(funzioni_utili.stile_checkbox())
        self.section_switcher.stateChanged.connect(self.switch_section)

        self.register_label.setFont(QFont("Times Roman", 11, QFont.Bold))
        self.register_label.setStyleSheet("color: green")

        switcher_layout.addWidget(self.login_label)
        switcher_layout.addWidget(self.section_switcher)
        switcher_layout.addWidget(self.register_label)

        switcher_container = QVBoxLayout()
        switcher_container.addLayout(switcher_layout)
        switcher_container.setAlignment(Qt.AlignCenter)

        self.stacked_widget.setFixedWidth(600)  # Imposta dimensioni fisse per il QStackedWidget

        # Centra il QStackedWidget orizzontalmente e verticalmente
        stacked_container = QVBoxLayout()
        stacked_container.addWidget(self.stacked_widget, alignment=Qt.AlignCenter)
        stacked_container.setAlignment(Qt.AlignCenter)

        outer_layout.addLayout(stacked_container)

        outer_layout.addLayout(switcher_container)

        # Login section
        login_widget = QWidget()
        self.init_login_ui(login_widget)
        self.stacked_widget.addWidget(login_widget)

        # Registrati section
        registrati_widget = QWidget()
        self.init_registrati_ui(registrati_widget)
        self.stacked_widget.addWidget(registrati_widget)

        funzioni_utili.center(self)

    ''''
    Configure the UI for login
    '''

    def init_login_ui(self, widget):
        main_layout = QVBoxLayout(widget)

        welcome_label = QLabel('Benvenuto!')

        form_layout = QFormLayout()

        form_container = QVBoxLayout()

        funzioni_utili.config_widget(
            main_layout, welcome_label, form_layout, form_container, 100
        )

        funzioni_utili.add_field_to_form(
            self.username_label, self.username_input, form_layout)

        self.password_input.setEchoMode(QLineEdit.Password)
        funzioni_utili.add_field_to_form(
            self.password_label, self.password_input, form_layout)


        main_layout.addLayout(form_container)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        self.login_button.clicked.connect(lambda: self.accedi())
        funzioni_utili.insert_button(self.login_button, button_layout)

        self.guest_button.clicked.connect(self.entra_guest)
        funzioni_utili.insert_button(self.guest_button, button_layout)

        main_layout.addLayout(button_layout)

        self.logo.setPixmap(QPixmap("presentation\\resources\\logo_trasparente.png"))
        self.logo.setScaledContents(True)
        self.logo.setFixedSize(300, 300)
        main_layout.addWidget(self.logo, alignment=Qt.AlignCenter)

    '''
    Configure the UI for registration
    '''

    def init_registrati_ui(self, widget):
        main_layout = QVBoxLayout(widget)

        registrati_label = QLabel('Registrati!')

        form_layout = QFormLayout()

        form_container = QVBoxLayout()

        funzioni_utili.config_widget(
            main_layout, registrati_label, form_layout, form_container, 100
        )

        funzioni_utili.add_field_to_form(
            self.username_label_, self.username_input_, form_layout)

        self.tipo_input.addItems([
            'Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore'
        ])
        funzioni_utili.add_field_to_form(self.tipo_label, self.tipo_input, form_layout)

        funzioni_utili.add_field_to_form(
            self.indirizzo_label, self.indirizzo_input, form_layout)

        self.password_input_.setEchoMode(QLineEdit.Password)
        funzioni_utili.add_field_to_form(
            self.password_label_, self.password_input_, form_layout)

        self.conferma_password_input.setEchoMode(QLineEdit.Password)
        funzioni_utili.add_field_to_form(
            self.conferma_password_label, self.conferma_password_input, form_layout)

        for psw in self.password:
            self.icons_action.append(QAction(QIcon("presentation\\resources\\pass_invisibile.png"), "", psw))
        for index, psw in enumerate(self.password):
            self.icons_action[index].triggered.connect(self.change_password_visibility)
            psw.addAction(self.icons_action[index], QLineEdit.TrailingPosition)

        main_layout.addLayout(form_container)

        main_layout.addWidget(self.tcu_cb, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.tcu, alignment=Qt.AlignCenter)

        self.tcu.setStyleSheet("color: blue; text-decoration: underline;")
        self.tcu.mousePressEvent = self.on_tcu_click

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        self.register_button.clicked.connect(self.registrati)
        funzioni_utili.insert_button(self.register_button, button_layout)

        main_layout.addLayout(button_layout)

    def on_tcu_click(self, event):
        QMessageBox.warning(
            self, "SupplyChain", f"Termini e condizioni d'uso work in progress!{event}")

    '''
    Changed between login and registration
    '''

    def switch_section(self, state):
        if state == Qt.Checked:
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.stacked_widget.setCurrentIndex(0)

    '''
    Administer the authentication
    '''

    def accedi(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            # Verifica le credenziali dell'utente
            login_success = self.controller.login(username, password)
        
            if login_success:
                QMessageBox.information(self, "SupplyChain", "Accesso effettuato correttamente!")

                # Ottieni i dati dell'utente dalla sessione dopo il login
                session_user = Session().current_user
                
                # Procedi con il resto del login come prima
                if session_user["role"] == 'Certificatore':
                    self.home_certificatore = HomePageCertificatore(self.reset)
                    self.home_certificatore.show()
                else:
                    # Passa il dizionario session_user invece dell'oggetto CompanyModel
                    self.home_page = HomePage(self.reset, session_user)
                    self.home_page.show()

                self.setVisible(False)  # Nascondi la finestra di login       

        except Exception as e:
            QMessageBox.warning(self, "SupplyChain", f"{e}")
    

    def entra_guest(self):
        self.home_guest = HomePageGuest(self.reset)
        QMessageBox.information(
            self, "EdilGest", "Puoi entrare come guest!")
        self.home_guest.show()
        self.close()

    '''
    Allow the user to register
    '''

    def registrati(self):
        if not self.tcu_cb.isChecked():
            QMessageBox.warning(
                self, "SupplyChain", "Devi accettare i termini e le condizioni d'uso!")
        else:
            username = self.username_input_.text()
            password = self.password_input_.text()
            conferma_password = self.conferma_password_input.text()
            tipo = self.tipo_input.currentText()
            indirizzo = self.indirizzo_input.text()

            if funzioni_utili.is_blank([
                username, password, conferma_password, tipo, indirizzo
            ]):
                QMessageBox.warning(
                    self, "SupplyChain", "Completare tutti i campi!")
            elif password != conferma_password:
                QMessageBox.warning(
                    self, "SupplyChain", "Conferma password errata!")
            else:
                try:

                    self.apri_html(
                        username=username, password=password,
                        tipo=tipo, indirizzo=indirizzo)
                    QMessageBox.information(
                        self, "SupplyChain", "Registrazione in corso...")
                except Exception as e:
                    QMessageBox.warning(
                        self, "SupplyChain", f"Errore durante la registrazione: {e}")
        

    '''
    Allow the user to change the password visibility
    '''

    def change_password_visibility(self):
        self.password_visibile = not self.password_visibile
        if not self.password_visibile:
            for index, p in enumerate(self.password):
                p.setEchoMode(QLineEdit.Password)
                self.icons_action[index].setIcon(QIcon("presentation\\resources\\pass_invisibile.png"))
        else:
            for index, p in enumerate(self.password):
                p.setEchoMode(QLineEdit.Normal)
                self.icons_action[index].setIcon(QIcon("presentation\\resources\\pass_visibile.png"))

    ''''
    Resets input fields
    '''

    def reset(self):
        self.tcu_cb.setChecked(False)
        self.username_input.setText("")
        self.password_input.setText("")
        self.username_input_.setText("")
        self.indirizzo_input.setText("")
        self.password_input_.setText("")
        self.conferma_password_input.setText("")
        self.otp_input.setText("")
        self.password_visibile = False
        self.setVisible(True)


#############################################################################################################


    def apri_html(self, tipo, indirizzo, username, password):
            try:

                UserModel.validate_password(password)
                hash_psw = UserModel.hash_password(password)
            except Exception as e:
                raise e
            dati = {
                "tipo": tipo,
                "indirizzo": indirizzo,
                "username": username,
                "password": hash_psw
            }

            url = f"http://localhost:5000/firma.html?tipo={dati['tipo']}&indirizzo={dati['indirizzo']}&username={dati['username']}&password={dati['password']}"
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            proc = subprocess.Popen([chrome_path, url])
            proc.wait()


            self.section_switcher.setChecked(False)  # Switch alla schermata di login
            self.reset()  # Reset dei campi
            QMessageBox.information(
                self, 
                "SupplyChain", 
                "Registrazione completata! Ora puoi effettuare il login con le tue credenziali."
            )
