# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Lotto:
    id_lotto: int
    tipo: str
    quantita: int
    cons_co2: int
    composizione: list["Composizione"] = field(default_factory=list)
    uc_co2 = int
    co2_costo_composizione : int = 0
    co2_totale_lotto : int = 0

    def __init__(self, id_lotto, tipo, quantita, consumo_co2):
        self.id_lotto = id_lotto
        self.tipo = tipo
        self.quantita = quantita
        self.cons_co2 = consumo_co2
        self.composizione = []
        



    def get_costo_totale_lotto_unitario(self):
        self.co2_costo_composizione = 0
        if  self.composizione.__len__:
            for comp in self.composizione:
                self.co2_costo_composizione += comp.get_co2_consumata_quantità_utilizzata()
        self.co2_totale_lotto_unitario = int((self.co2_costo_composizione + self.cons_co2 ) / self.quantita)

        return self.co2_totale_lotto_unitario 


    

@dataclass
class Composizione:
    id_lotto_input: int
    quantita_utilizzata: int
    lotto_input: Optional[Lotto] = None

    def __init__(self, id_lotto_input, quantita_utilizzata, lotto_input=None):
        self.id_lotto_input = id_lotto_input
        self.quantita_utilizzata = quantita_utilizzata
        self.lotto_input = lotto_input

    def get_co2_consumata_quantità_utilizzata(self) -> int:
        if isinstance(self.lotto_input,Lotto):
            return self.lotto_input.get_costo_totale_lotto_unitario() * self.quantita_utilizzata
        else :
            return 0
        


        