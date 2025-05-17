# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from dataclasses import dataclass
import hashlib
import re

from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError


@dataclass
class UserModel:
    """
    Data Transfer Object (DTO) for user authentication.
    """
    id_credential: int
    username: str
    password: str
    topt_secret: str

    def __init__(self,id_credenziali,username,password):
        self.id_credential = id_credenziali
        self.username =username
        self.password = password         

    @staticmethod
    def validate_password(password : str):
        if len(password) < 8:
                raise PasswordTooShortError("La password deve contenere almeno 8 caratteri!")

        # Controllo complessità con regex
        if not re.search(r'[A-Z]', password):  # Almeno una lettera maiuscola
            raise PasswordWeakError("La password deve contenere almeno una lettera maiuscola.")
        if not re.search(r'[a-z]', password):  # Almeno una lettera minuscola
            raise PasswordWeakError("La password deve contenere almeno una lettera minuscola.")
        if not re.search(r'[0-9]', password):  # Almeno un numero
            raise PasswordWeakError("La password deve contenere almeno un numero.")
        if not re.search(r'\W', password):  # Almeno un carattere speciale
            raise PasswordWeakError("La password deve contenere almeno un carattere speciale (!, @, #, etc.).")
        
    @staticmethod
    def hash_password(password: str) -> str:
        """Restituisce un hash SHA-256 della password."""
        return hashlib.sha256(password.encode()).hexdigest()

