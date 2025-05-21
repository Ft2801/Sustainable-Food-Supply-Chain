# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace

from configuration.log_load_setting import logger
from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError
from domain.exception.database_exceptions import UniqueConstraintError, DatabaseError
from domain.exception.login_exceptions import HaveToWaitException, ToManyTryLogEXcepition , LoginFailExetion
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from session import Session
from model.company_model import CompanyModel
from model.credential_model import UserModel

class ControllerAutenticazione:

    def __init__(self):
        self.credential = CredentialRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")
        self.sessione = Session()

    def registrazione(self, username, password, tipo, indirizzo):
        """Tenta di aggiungere un utente, gestendo eventuali errori."""
        try:
            self.credential.register(username, password, tipo, indirizzo)
            return True, "Utente registrato con successo!", None # Aggiunto None per coerenza
        except PasswordTooShortError as e:
            return False, str(e), None
        except PasswordWeakError as e:
            return False, str(e), None
        except UniqueConstraintError:
            return False, "Errore: Username già esistente.", None
        except DatabaseError:
            return False, "Errore nel database.", None
        # R1710: implicito return None se nessuna eccezione sopra viene sollevata
        # e il try ha successo, ma era return True, "messaggio".
        # Per coerenza tutti i return dovrebbero avere 3 elementi.

    def login(self, username, password, otp_code=None): # W0613 otp_code non usato
        try:
            self.sessione.can_log()
            credenziali = self.credential.get_user(username)

            if credenziali is not None:
                if credenziali.password == UserModel.hash_password(password):
                    try:
                        azienda = self.credential.get_azienda_by_id(credenziali.id_credential)
                        self.sessione.start_session(azienda)
                        logger.info(f"Username {username} ha eseguito l'accesso")
                        return True # R1710: Coerenza dei return
                    except Exception as e:
                        logger.warning(f"Errore durante la creazione dellla sessione: {str(e)}")
                        return False # R1710: Coerenza dei return
                else:
                    # Password errata, gestita dall'eccezione LoginFailExetion nel blocco except esterno
                    raise LoginFailExetion("Password errata")
            else:
                # Utente non trovato, gestito dall'eccezione LoginFailExetion nel blocco except esterno
                raise LoginFailExetion("Utente non trovato")

        except HaveToWaitException as e:
            raise e
        except ToManyTryLogEXcepition as e:
            raise e
        except LoginFailExetion as e: # Cattura esplicita di LoginFailExetion
            logger.warning(f"Tentativo di login fallito: {str(e)}")
            logger.info(f"Tentativi di login: {self.sessione.tentativi}")
            raise e # Rilancia l'eccezione LoginFailExetion specifica
        except Exception as e: # W0719: Cattura eccezione generica
            logger.warning(f"Errore generico durante il login: {str(e)}")
            logger.info(f"Tentativi di login: {self.sessione.tentativi}")
            raise LoginFailExetion(f"Errore imprevisto: {str(e)}") from e # W0707

    def get_user(self) -> CompanyModel:
        try:
            
            return self.credential.get_azienda_by_id(Session().current_user["id_azienda"])
        except Exception as e: # W0719: Cattura eccezione generica
            logger.error(f"Errore nel'ottenimento del utente {e}")
            raise Exception(f"Errore nel recupero utente: {str(e)}") from e # W0707

    def verifica_password(self, old_password: str) -> bool:
        try:
            
            return self.credential.verifica_password(old_password, Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Eccezione {e}")
            return False

    def cambia_password(self, password: str):
        try:
            
            self.credential.cambia_password(password, Session().current_user["id_azienda"])
        except Exception as e: # W0719: Cattura eccezione generica
            # W0707: Aggiunto 'from e'
            raise Exception(f"Errore durante il cambio password: {str(e)}") from e
# C0304: Aggiunta newline finale
