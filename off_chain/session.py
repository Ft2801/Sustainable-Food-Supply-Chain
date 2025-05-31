from model.company_model import CompanyModel
import time

from domain.exception.login_exceptions import HaveToWaitException, ToManyTryLogEXcepition
class Session:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._current_user: CompanyModel = None  # Rende l'attributo privato
        self.logged_in = False
        self.start_app = time.strftime("%Y/%m/%d/%H-%M")
        self.session_start_time = None
        self.session_timeout = 3600
        self.session_token = None
        self.tentativi = 1
        self.timer = 0
        self.numero_tentativi = 6

    def start_session(self, user_data: CompanyModel):
        """Avvia una nuova sessione"""
        self._current_user = user_data
        self.logged_in = True
        self.session_start_time = time.time()
        self.tentativi = 1
        self.timer = 0
        self.session_token = f"token_{int(self.session_start_time)}"
        return self.session_token

    def end_session(self):
        """Termina la sessione e pulisce i dati"""
        self._current_user = None
        self.logged_in = False
        self.session_start_time = None
        self.session_token = None

    def add_try(self):
        self.tentativi += 1
        
    def can_log(self):
        self.add_try()
        self.check_tentativi()
    
    def check_tentativi(self):
        if self.tentativi  < self.numero_tentativi:
           return
        if self.tentativi == self.numero_tentativi:
            self.timer = time.time() + 30
            raise ToManyTryLogEXcepition()
        if self.tentativi > self.numero_tentativi:
            secondi_mancanti = time.time() - self.timer
            if secondi_mancanti > 0:
                self.tentativi = 1
                return
            raise HaveToWaitException(str(secondi_mancanti))

    def is_authenticated(self):
        """Verifica se la sessione è ancora valida"""
        if not self.logged_in:
            return False
        if self.session_start_time and time.time() - self.session_start_time > self.session_timeout:
            self.end_session()
            return False
        return True

    @property
    def current_user(self):
        """Restituisce una copia sicura dell'utente, senza informazioni sensibili"""
        if self.logged_in:
            return {
                "id": self._current_user.id_azienda,
                "username": self._current_user.nome,
                "role": self._current_user.tipo,
                "id_azienda" : self._current_user.id_azienda,
                "token": self._current_user.token,

                 # Solo info essenziali
            }
        return None
