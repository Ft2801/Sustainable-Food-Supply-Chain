import datetime
from dataclasses import dataclass


@dataclass
class CertificationModel:
    """
    Data model for transporting product information between layers.
    """
    id_certificato: int
    id_lotto: int
    descrizione_certificato: str
    nome_azienda: str
    data_certificato: datetime

