from dataclasses import dataclass, field
from model.componente_model import Componente

@dataclass
class ProductModel:
    """
    Data model for transporting product information between layers.
    """
    Id_prodotto: int
    Nome_prodotto: str
    componenti: list[Componente] = field(default_factory=list)


