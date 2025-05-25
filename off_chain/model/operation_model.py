import datetime
from dataclasses import dataclass


@dataclass
class OperationModel:
    """
    Data model for transporting product information between layers.
    """
    Id_operazione: int
    Id_prodotto: int
    Quantita_prodotto: int
    Nome_prodotto: str
    Data_operazione: datetime
    Consumo_co2_operazione: int
    Nome_operazione: str
    Nome_azienda: str
   
