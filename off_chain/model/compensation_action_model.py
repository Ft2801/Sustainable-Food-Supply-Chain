import datetime
from dataclasses import dataclass


@dataclass
class CompensationActionModel:
    """
    Model for CompensationActionModel.
    """
    id_azione: int = None
    data_azione: datetime = None
    id_azienda: int = None
    co2_compensata: int = None
    nome_azione: str = None
    blockchain_registered: bool = False  # Indica se l'azione è registrata sulla blockchain


