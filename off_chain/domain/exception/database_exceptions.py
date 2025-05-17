class DatabaseError(Exception):
    """Eccezione generale per errori del database"""
    pass


class UniqueConstraintError(DatabaseError):
    """Eccezione per violazione del vincolo di unicità"""
    pass
