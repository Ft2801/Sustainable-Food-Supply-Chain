from enum import Enum

class aziende_enum(Enum):

    RIVENDIORE  = "Rivenditore",
    CERIFICATORE  = "Certificatore",
    TRASPORTATORE = "Trasportatore",
    PRODUTTORI  = "Agricola"


class ordinamento (Enum):
    CRESCENTE = "ASC"
    DECRESCENTE = "DESC"   
