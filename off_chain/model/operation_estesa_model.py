# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from dataclasses import dataclass
import datetime
from model.operation_model import OperationModel
from model.product_model import ProductModel

@dataclass
class OperazioneEstesaModel:

    id_operazione: int
    id_lotto: int
    nome_operazione: str
    data_operazione: datetime
    id_prodotto : int
    nome_prodotto : str
    quantita_prodotto : int
    consumo_co2 : int
    blockchain_registered: bool = False  # Indica se l'operazione è registrata sulla blockchain
    descrizione : str = ""  # Campo per la descrizione aggiuntiva del prodotto
    

    
   
