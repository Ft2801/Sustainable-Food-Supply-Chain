class LoginFailExetion(Exception):
    """Eccezione sollevata quando la quantità disponibile è insufficiente."""
    def __init__(self, msg=None):
        message = f"Login fallito: {msg}" if msg else "Login fallito: credenziali errate"
        super().__init__(message)

class ToManyTryLogEXcepition(Exception):
    """Eccezione sollevata quando la quantità disponibile è insufficiente."""
    def __init__(self,):
        super().__init__(f"Login fallito: troppi tentativi")

class HaveToWaitException(Exception):
    def __init__(self, msg : str):
        super().__init__(f"Login inattivo per: {msg} secondi")
