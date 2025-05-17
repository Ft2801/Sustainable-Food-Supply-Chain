from dataclasses import dataclass


@dataclass
class ProdottoLottoModel:
    id_prodotto : int
    id_azienda : int
    quantita : int
    nome : str
    id_lotto : int

    