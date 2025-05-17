from dataclasses import dataclass, field

@dataclass
class ProductStandardModel:
    """
    Data model for transporting product information between layers.
    """
    Id_prodotto: int
    Nome_prodotto: str