# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import datetime
from dataclasses import dataclass


@dataclass
class RichiestaModel:
    """
    Data model for transporting product information between layers.
    """
    id_richiesta: int
    id_azienda_richiedente: int
    nome_azienda_richiedente: str
    id_azienda_ricevente: int
    nome_azienda_ricevente: str
    id_azienda_trasportatore: int
    nome_azienda_trasportatore: str
    id_prodotto: int
    nome_prodotto: str
    quantita: float
    stato_ricevente: str
    stato_trasportatore: str
    data: datetime.datetime
    id_lotto_input: int
    
   
