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
from presentation.controller.blockchain_controller import BlockchainController

class ControllerAutenticazione:

    def __init__(self):
        self.credential = CredentialRepositoryImpl()
        self.blockchainconroller = BlockchainController()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")
        self.sessione = Session()

    def registrazione(self, username, password, tipo, indirizzo, blockchain_address : str):
        """Tenta di aggiungere un utente, gestendo eventuali errori."""
        try:

            self.credential.register(username, password, tipo, indirizzo,blockchain_address)
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
            raise Exception(f"Errore nel recupero utente nella funzione getuser: {str(e)}") from e # W0707

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
            
    def get_id_by_address(self, blockchain_address: str) -> int:
        """
        Ottiene l'ID dell'azienda a partire dall'indirizzo blockchain.
        
        Args:
            blockchain_address: L'indirizzo blockchain dell'azienda
            
        Returns:
            int: L'ID dell'azienda, o None se non trovato
        """
        try:
            # Normalizza l'indirizzo per garantire corrispondenza case-insensitive
            blockchain_address = blockchain_address.lower()
            
            # Ottieni l'ID dell'azienda dal database
            query = "SELECT a.Id_azienda FROM Azienda a JOIN Credenziali c ON a.Id_credenziali = c.Id_credenziali WHERE LOWER(c.address) = ?"
            params = (blockchain_address,)
            
            # Esegui la query
            result = self.credential.db.fetch_one(query, params)
            
            if result:
                logger.info(f"Trovato ID azienda {result} per l'indirizzo blockchain {blockchain_address}")
                return result
            else:
                logger.warning(f"Nessun ID azienda trovato per l'indirizzo blockchain {blockchain_address}")
                return None
        except Exception as e:
            logger.error(f"Errore durante il recupero dell'ID azienda dall'indirizzo blockchain: {str(e)}")
            return None
# C0304: Aggiunta newline finale
