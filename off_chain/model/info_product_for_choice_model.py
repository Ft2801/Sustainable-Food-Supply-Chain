from dataclasses import dataclass


@dataclass
class ProductForChoiceModel:
    
    nome_azienda: str
    nome_prodotto: str
    quantita: int
    id_prodotto: int
    id_azienda: int
    co2: int

    