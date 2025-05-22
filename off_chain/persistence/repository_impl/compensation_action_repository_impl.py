# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespaces
import datetime
from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from persistence.query_builder import QueryBuilder
from model.compensation_action_model import CompensationActionModel


class CompensationActionRepositoryImpl( ABC):
    # Class variable that stores the single instance
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()




    def get_lista_azioni(self, id_azienda: int,  data_start: datetime = None, data_end: datetime = None, ordinamento: str = None) -> list[CompensationActionModel]:
        try:


            self.query_builder.select("Id_azione","Id_azienda","Data","Co2_compensata","Nome_azione","blockchain_registered").table("Azioni_compensative").where("Id_azienda", "=", id_azienda)

            if data_start and data_end:
                self.query_builder.where("Data", ">", data_start).where("Data", "<", data_end)
                
            if ordinamento:
                self.query_builder.order_by("Co2_compensata", "DESC")

            query,value = (
                self.query_builder.get_query()
            )
            results = self.db.fetch_results(query, value)
            lista_op= [
                    CompensationActionModel(
                        id_azione=row[0],
                        id_azienda=row[1],
                        data_azione=row[2],
                        co2_compensata=row[3],
                        nome_azione=row[4],
                        blockchain_registered=bool(row[5]) if len(row) > 5 else False,
                )
                for row in results
                ]

            return lista_op
        except Exception as e:
            logger.error(f"Errore nel recuero delle azioni compensative: {e}")
            return []
    

    def get_co2_compensata(self, id_azienda: int) -> float:
        query,value = (
            self.query_builder
                .select("SUM(Co2_compensata)")
                .table("Azioni_compensative")
                .where("Id_azienda", "=", id_azienda)
        )
        try:
            return float(self.db.fetch_one(query, value))
        except:
            raise ValueError

    def inserisci_azione(self, data: datetime, azienda: int, co2_compensata: str, nome_azione: str):
        try:

            queries = []
            query_azione = """
            INSERT INTO Azioni_compensative (Data, Id_azienda, Co2_compensata, Nome_azione)
            VALUES (?, ?, ?, ?);
            """
            value_azione =(data,azienda,co2_compensata, nome_azione)
            queries.append((query_azione, value_azione))

            # Aggiorna la CO2 compensata dell'azienda
            query_update_co2=""" UPDATE Azienda SET Co2_compensata = Co2_compensata + ? 
            WHERE Id_azienda = ?;"""
            value_update_co2 = (co2_compensata, azienda)
            queries.append((query_update_co2, value_update_co2))
            
            # Aggiorna anche i token dell'azienda (1 token per ogni unità di CO2 compensata)
            query_update_token=""" UPDATE Azienda SET Token = Token + ? 
            WHERE Id_azienda = ?;"""
            value_update_token = (int(co2_compensata), azienda)
            queries.append((query_update_token, value_update_token))


            self.db.execute_transaction(queries)
            logger.info("Azione compensativa aggiunta con successo")

        except Exception as e:
            logger.error(f"Errore nel inserimento di una azione compensativa {e}")
            raise Exception(f"{e}")

