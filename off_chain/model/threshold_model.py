from dataclasses import dataclass


@dataclass
class ThresholdModel:
    """
    Represents operation thresholds for products.
    """
    Prodotto: str
    Soglia_Massima: float
    Tipo: str
    
