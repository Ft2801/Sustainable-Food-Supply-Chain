class RichiestaTokenModel:
    id_richiesta : int
    mittente :  str
    destinatario : str
    quantita : int
    stato : str

    def __init__(self, mittente: str, destinatario: str, quantita: int, stato: str):
        self.mittente = mittente
        self.destinatario = destinatario
        self.quantita = quantita
        self.stato = stato
