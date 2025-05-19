# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import sqlite3
from configuration.database import Database
from model.richiesta_model import RichiestaModel
from model.richiesta_token_model import RichiestaTokenModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl import db_default_string
from configuration.log_load_setting import logger

class RichiesteRepositoryImpl():
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def inserisci_richiesta(self, id_az_richiedente: int,id_az_ricevente: int,id_az_trasporto: int, id_prodotto: int, quantita: int) :
        """
        Inserisce una nuova richiesta di prodotto nel database.
        """
        self.query_builder.table("Richiesta").insert(
            id_richiedente = id_az_richiedente,
            id_ricevente = id_az_ricevente,
            id_trasportatore = id_az_trasporto,
            id_prodotto = id_prodotto,
            quantita = quantita,
            stato_ricevente="In attesa",
            stato_trasportatore="In attesa",

        )
        query, value = self.query_builder.get_query()
        try:
            self.db.execute_query(query, value)
            
        except Exception as e:
            logger.error(f"Errore nell'inserimento della richiesta: {e}", exc_info=True)

    def get_richieste_ricevute(self, id_azienda: int, check_trasporto: bool = False) -> list:
        try:
            
            self.query_builder \
                .select(
                    "r.Id_richiesta",
                    "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                    "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                    "r.Id_trasportatore", "tras.Nome AS Nome_trasportatore",
                    "r.Id_prodotto", "prod.Nome AS Nome_prodotto",
                    "r.Quantita", "r.Stato_ricevente",
                    "r.Stato_trasportatore", "r.Data"
                ) \
                .table("Richiesta AS r") \
                .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente") \
                .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente") \
                .join("Azienda AS tras", "tras.Id_azienda", "r.Id_trasportatore") \
                .join("Prodotto AS prod", "prod.Id_prodotto", "r.Id_prodotto")

            # Filtro condizionato
            if not check_trasporto:
                self.query_builder.where("r.Id_ricevente", "=", id_azienda)  
            else:
                self.query_builder.where("r.Stato_ricevente", "=", db_default_string.STATO_ACCETTATA)
                self.query_builder.where("r.Id_trasportatore", "=", id_azienda)

            query, value = self.query_builder.get_query()
            risultati_raw = self.db.fetch_results(query, value)

            if not risultati_raw:
                logger.info(f"Nessuna richiesta ricevuta trovata per l'azienda con ID {id_azienda}.")
                return []

            risultati = []
            for r in risultati_raw:
                id_prodotto = r[7]  # Posizione di Id_prodotto nella tupla

                # Recupera Id_lotto SOLO se op.Tipo è produzione o trasformazione
                query_lotto = """
                    SELECT Id_lotto 
                    FROM Operazione 
                    WHERE Id_prodotto = ? 
                    AND (Tipo = ? OR Tipo = ?)
                    ORDER BY Id_operazione DESC LIMIT 1;
                """
                res_lotto = self.db.fetch_one(query_lotto, (id_prodotto,db_default_string.TIPO_OP_PRODUZIONE,
                                                            db_default_string.TIPO_OP_TRASFORMAZIONE))
                id_lotto = res_lotto if res_lotto is not None else None

                risultati.append(RichiestaModel(*r, id_lotto))

            logger.info(f"Richieste ricevute per l'azienda con ID {id_azienda}: {risultati}")
            return risultati

        except Exception as e:
            logger.error(f"Errore nel recupero delle richieste ricevute: {e}", exc_info=True)
            return []

        
    def get_richieste_effettuate(self, id_azienda: int) -> list[RichiestaModel]:
        """
        Restituisce tutte le richieste effettuate da un'azienda.
        """
        try:
            # 1. Recupera le richieste
            query, value = (
                self.query_builder
                    .select(
                        "r.Id_richiesta",
                        "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                        "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                        "r.Id_trasportatore", "tras.Nome AS Nome_trasportatore",
                        "r.Id_prodotto", "prod.Nome AS Nome_prodotto",
                        "r.Quantita", "r.Stato_ricevente",
                        "r.Stato_trasportatore", "r.Data"
                    )
                    .table("Richiesta AS r")
                    .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente")
                    .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente")
                    .join("Azienda AS tras", "tras.Id_azienda", "r.Id_trasportatore")
                    .join("Prodotto AS prod", "prod.Id_prodotto", "r.Id_prodotto")
                    .where("r.Id_richiedente", "=", id_azienda)
                    .get_query()
            )
            richieste = self.db.fetch_results(query, value)

            if not richieste:
                logger.info(f"Nessuna richiesta effettuata trovata per l'azienda con ID {id_azienda}.")
                return []

            risultati = []
            for r in richieste:
                id_prodotto = r[7]  # posizione di Id_prodotto nella tupla
                query_lotto = """
                    SELECT Id_lotto 
                    FROM Operazione 
                    WHERE Id_prodotto = ? AND Tipo != ?
                    ORDER BY Id_operazione DESC LIMIT 1;
                """
                res_lotto = self.db.fetch_one(query_lotto, (id_prodotto,db_default_string.TIPO_OP_TRASPORTO))
                id_lotto = res_lotto if res_lotto is not None else None

                risultati.append(RichiestaModel(*r, id_lotto))

            return risultati

        except Exception as e:
            logger.error(f"Errore nel recupero delle richieste effettuate: {e}", exc_info=True)
            return []

        
    def update_richiesta(self, id_richiesta: int, nuovo_stato: str,azienda_role : str) -> None:
        """
        Aggiorna lo stato di una richiesta.
        """
        self.query_builder.table("Richiesta").where("Id_richiesta", "=", id_richiesta)
        if azienda_role == db_default_string.TIPO_AZIENDA_TRASPORTATORE:
            self.query_builder.update(
                Stato_trasportatore=nuovo_stato
            )
        elif azienda_role == db_default_string.TIPO_AZIENDA_AGRICOLA or azienda_role == db_default_string.TIPO_AZIENDA_TRASFORMATORE:
            self.query_builder.update(
                Stato_ricevente=nuovo_stato
            )
        else:
            logger.error(f"Ruolo aziendale non valido: {azienda_role}.")
            raise ValueError("Ruolo aziendale non valido.")

        query, value = self.query_builder.get_query()
        try:
            self.db.execute_query(query, value)
            logger.info(f"Richiesta con ID {id_richiesta} aggiornata a {nuovo_stato}.")
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento della richiesta: {e}", exc_info=True)

            
    def get_richieste_ric_token(self, id_azienda: int) -> list[RichiestaTokenModel]:

        try:
            self.query_builder.select(
                "r.Id_richiesta",
                "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                "r.Quantita", "r.Stato"
            )\
            .table("RichiestaToken AS r") \
            .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente") \
            .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente") \
            .where("r.Id_ricevente", "=", id_azienda) \
            .where("r.Stato", "=", db_default_string.STATO_ATTESA)
            query, value = self.query_builder.get_query()
            risultati_raw = self.db.fetch_results(query, value)

            return [RichiestaTokenModel(*r) for r in risultati_raw]
        except Exception as e:
            logger.error(f"Errore nel recupero delle richieste di token: {e}", exc_info=True)
            return []
    
    def get_richiesta_inviata_token(self, id_azienda: int) -> list[RichiestaTokenModel]:

        try:
            self.query_builder.select(
                "r.Id_richiesta",
                "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                "r.Quantita", "r.Stato"
            )\
            .table("RichiestaToken AS r") \
            .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente") \
            .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente") \
            .where("r.Id_richiedente", "=", id_azienda)
            query, value = self.query_builder.get_query()
            risultati_raw = self.db.fetch_results(query, value)

            return [RichiestaTokenModel(*r) for r in risultati_raw]
        except Exception as e:
            logger.error(f"Errore nel recupero delle richieste di token inviate: {e}", exc_info=True)
            return []
    
    def get_operazioni_token(self, id_azienda: int) -> list[RichiestaTokenModel]:

        try:
            self.query_builder.select(
                "r.Id_richiesta",
                "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                "r.Quantita", "r.Stato"
            )\
            .table("RichiestaToken AS r") \
            .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente") \
            .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente") \
            .where("r.Stato", "=", db_default_string.STATO_ACCETTATA)\
            .or_where("r.Id_richiedente", "=", id_azienda) \
            .or_where("r.Id_ricevente", "=", id_azienda) 
            

            query, value = self.query_builder.get_query()
            risultati_raw = self.db.fetch_results(query, value)

            print(f"risultati_raw {risultati_raw}")

            return [RichiestaTokenModel(*r) for r in risultati_raw] if risultati_raw else []
        except Exception as e:
            logger.error(f"Errore nel recupero delle operazioni di token: {e}", exc_info=True)
            return []
    
    def update_richiesta_token(self, richiesta: RichiestaTokenModel, stato : str) -> None:
        """
        Aggiorna lo stato di una richiesta.
        """
        try:
            queries = []

            # Aggiornamento
            query_mag = """UPDATE RichiestaToken SET stato = ? WHERE id_richiesta = ?;""" 
            value_mag = (stato, richiesta.id_richiesta)
            queries.append((query_mag, value_mag))

            query_mag = """UPDATE Azienda SET Token = Token - ? WHERE Id_azienda = ?;""" 
            value_mag = (richiesta.quantita, richiesta.id_destinatario)
            queries.append((query_mag, value_mag))

            query_mag = """UPDATE Azienda SET Token = Token + ? WHERE Id_azienda = ?;""" 
            value_mag = (richiesta.quantita, richiesta.id_mittente)
            queries.append((query_mag, value_mag))

            self.db.execute_transaction(queries)
            logger.info(f"Richiesta con ID {richiesta.id_richiesta} aggiornata a {stato}.")

        
        except sqlite3.IntegrityError as e:
            logger.error(f"Errore di integrità nel database: {e}", exc_info=True)
            raise ValueError("Non disponi di qui token")
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento della richiesta: {e}", exc_info=True)
            return False
        
    def send_richiesta_token(self, mittente: int, destinatario: int , quantita : int) -> None:
        """
        Invia una richiesta di token.
        """
        try:
            self.query_builder.table("RichiestaToken").insert(
                id_richiedente = mittente,
                id_ricevente = destinatario,
                quantita = quantita,
                stato = db_default_string.STATO_ATTESA
            )
            query, value = self.query_builder.get_query()
            self.db.execute_query(query, value)
            logger.info(f"Richiesta di token inviata con successo.")
        except Exception as e:
            logger.error(f"Errore nell'invio della richiesta di token: {e}", exc_info=True)

         