class RichiestaTokenModel:
    id_richiesta : int
    id_mittente : int
    id_destinatario : int
    mittente :  str
    destinatario : str
    quantita : int
    stato : str

    def __init__(self, id_richiesta : int ,id_mittente: int, \
                 mittente : str,  id_destinatario: int, destinatario: str, quantita: int, stato: str):
        self.mittente = mittente
        self.id_richiesta = id_richiesta
        self.id_mittente = id_mittente
        self.id_destinatario = id_destinatario
        self.destinatario = destinatario
        self.quantita = quantita
        self.stato = stato
