# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from model.threshold_model import ThresholdModel
from persistence.query_builder import QueryBuilder



class ThresholdRepositoryImpl(ABC):
    # Class variable that stores the single instance

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
   

    def get_lista_soglie(self) -> list[ThresholdModel]:
        self.query_builder.select("P.Nome","Soglia_Massima","Operazione").table("Soglie") \
                        .join("Prodotto AS P","P.Id_prodotto", "Prodotto")
    
            
        query, value = (self.query_builder.get_query() )

        try:
        
            return [ThresholdModel(*x) for x in self.db.fetch_results(query, value)]
    
        except Exception as err:
            logger.error(f"Errore durante il recupero delle soglie: {err}")
        return []
        
