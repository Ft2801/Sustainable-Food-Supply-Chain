from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class CompanyModel:
    """
    Data model for transporting company information between layers.
    """
    id_azienda: int
    id_credenziali: int
    tipo: str
    nome: str
    indirizzo: str
    co2_consumata: Optional[int] = None
    co2_compensata: Optional[int] = None
    token : int = 0
    data : datetime = None


