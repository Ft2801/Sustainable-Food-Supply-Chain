class PasswordTooShortError(Exception):
    """Eccezione per password con meno di 8 caratteri"""
    pass


class PasswordWeakError(Exception):
    """Eccezione per password che non soddisfa i criteri di sicurezza"""
    pass
