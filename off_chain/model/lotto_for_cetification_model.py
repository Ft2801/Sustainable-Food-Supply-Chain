from dataclasses import dataclass
import datetime


@dataclass
class LottoForCertificaion:
    id_lotto: int
    tipo_operazione : str
    data : datetime
    consumo_co2 : int
    nome_azienda : str
    nome_prodotto : str
