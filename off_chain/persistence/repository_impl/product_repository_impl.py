# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from model.prodotto_finito_model import ProdottoLottoModel
from model.info_product_for_choice_model import ProductForChoiceModel
from model.lotto_composizione_model import Composizione, Lotto
from model.prodotto_finito_cliente import ProdottoFinito
from model.product_standard_model import ProductStandardModel
from persistence.query_builder import QueryBuilder
from model.prodotto_finito_model import ProdottoLottoModel
from persistence.repository_impl import db_default_string


class ProductRepositoryImpl( ABC):
    """
     Implementing the prodotto repository.
     """
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def co2_consumata_prodotti(self, prodotti: [int]) -> list:
        lista_con_co2 = []
        for prodotto in prodotti:
            #repo = ProductRepositoryImpl()
            storico = self.get_storico_prodotto(prodotto[0])
            totale_co2 = sum(t[4] for t in storico)
            lista_con_co2.append((prodotto, totale_co2))
        return lista_con_co2


    def get_prodotti_standard_agricoli(self) ->list[ProductStandardModel]:
        try:
            result = self.db.fetch_results("SELECT Id_prodotto, Nome  FROM Prodotto WHERE  Stato = 0")
            print(result)
            return [ProductStandardModel(*x) for x in result] if result else []
        except Exception as e:
            logger.warning(f"Nessun prodotto trovato {e}")
            return[]
         

    def get_prodotti_standard_trasformazione(self)  -> list[ProductStandardModel]:
        try:
            result = self.db.fetch_results("SELECT Id_prodotto, Nome  FROM Prodotto WHERE  Stato = 1")
            print(f"risultao----{result}")
            return [ProductStandardModel(*x) for x in result] if result else []
        except Exception as e:
            logger.warning(f"Nessun prodotto trovato {e}")
            return[]




    """ Funzioni definitive"""

    def get_materie_prime_magazzino_azienda(self, id_azienda : int) -> list[ProdottoLottoModel]:
        query, value = (
            self.query_builder
            .select("Prodotto.id_prodotto","Magazzino.id_azienda","Magazzino.quantita", "Prodotto.nome", "Operazione.id_lotto")
            .table("Magazzino")
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto")
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto")
            .where("Magazzino.id_azienda", "=", id_azienda)
            .where("Prodotto.stato", "=", 0)  # Stato 0 indica che è una materia prima
            .get_query()
        )

        try:
            logger.info(f"Query in get_materie_prime_magazzino_azienda: {query} - Value: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as e:
            logger.error(f"Error in get_materie_prime_magazzino_azienda: {e}")
            return []

        
        if not result:
            logger.warning("The get_materie_prime_magazzino_azienda is empty or the query returned no results.")
        else:
            logger.info(f"Obtained in get_materie_prime_magazzino_azienda: {result}")
        try:
            return [ProdottoLottoModel(*x) for x in result] if result else [] 
        except Exception as e:
            logger.error(f"Error in converting result to ProdottoLottoModel: {e}")
            return []   
     # Assicurati che il path sia corretto


    def get_prodotti_finiti_magazzino_azienda (self, id_azienda : int) -> list[ProdottoLottoModel]:
        query, value = (
            self.query_builder
            .select("Prodotto.id_prodotto","Magazzino.id_azienda","Magazzino.quantita", "Prodotto.nome", "Operazione.id_lotto")
            .table("Magazzino")
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto")
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto")
            .where("Magazzino.id_azienda", "=", id_azienda)
            .where("Prodotto.stato", "=", 1)  # Stato 0 indica che è una materia prima
            .get_query()
        )

        try:
            logger.info(f"Query in get_prodotti_finiti_magazzino_azienda : {query} - Value: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as e:
            logger.error(f"Error in get_prodotti_finiti_magazzino_azienda: {e}")
            return []

        
        if not result:
            logger.warning("The get_prodotti_finiti_magazzino_azienda is empty or the query returned no results.")
        else:
            logger.info(f"Obtained in get_prodotti_finiti_magazzino_azienda: {result}")
        try:
            return [ProdottoLottoModel(*x) for x in result] if result else [] 
        except Exception as e:
            logger.error(f"Error in converting result to ProdottoLottoModel: {e}")
            return []


    def get_prodotti_ordinabili(self,tipo_prodoto : int = 0) -> list[ProductForChoiceModel]:
        
        self.query_builder \
            .select("Azienda.Nome","Prodotto.nome","Magazzino.quantita",
                    "Prodotto.id_prodotto","Azienda.Id_azienda",  "Operazione.Consumo_CO2") \
            .table("Magazzino") \
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto") \
            .join("Azienda", "Operazione.id_azienda", "Azienda.id_azienda") \
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto") \
            .where("Magazzino.quantita", ">", 0)
            
        if tipo_prodoto == 0:
            self.query_builder.where("Prodotto.stato", "=", 0)\
                             .where("Azienda.Tipo", "=", db_default_string.TIPO_AZIENDA_AGRICOLA)
        elif tipo_prodoto == 1:
            self.query_builder.where("Prodotto.stato", "=", 1) \
                            .where("Azienda.Tipo", "=", db_default_string.TIPO_AZIENDA_TRASPORTATORE)
        else:
            raise ValueError("Tipo di prodotto non identificato")



        query,value = self.query_builder.get_query()

        try:
            logger.info(f"Query in get_prodotti_ordinabili: {query} - Value: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as e:
            logger.error(f"Error in get_prodotti_ordinabili: {e}")
            return []

        
        if not result:
            logger.warning("The get_prodotti_ordinabili is empty or the query returned no results.")
        else:
            logger.info(f"Obtained in get_prodotti_ordinabili: {result}")
        try:
            return [ProductForChoiceModel(*x) for x in result] if result else []
        except Exception as e:
            logger.error(f"Error in converting result to ProductForChoiceModel: {e}")
            return []



# Funzione per caricare un lotto e la sua composizione ricorsiva
    def carica_lotto_con_composizione(self, id_lotto) -> Lotto:
    # 1. Recupero dati dell'operazione (lotto)
        query, value = (
            self.query_builder
            .select("Id_lotto", "Tipo", "quantita", "Consumo_CO2")
            .table("Operazione")
            .where("Id_lotto", "=", id_lotto)
            .get_query()
        )

        try:
            rows = self.db.fetch_results(query, value)
           
            if not rows:
                logger.warning(f"Nessuna operazione trovata per id_lotto: {id_lotto}")
                return None
            row = rows[0]
            lotto = Lotto(*row)  # Istanza singola
        except Exception as e:
            logger.error(f"Errore nel recupero dell'operazione: {e}")
            return None

        # 2. Recupero composizioni
        query, value = (
            self.query_builder
            .select("id_lotto_input", "quantità_utilizzata")
            .table("ComposizioneLotto")
            .where("id_lotto_output", "=", id_lotto)
            .get_query()
        )

        try:
            rows = self.db.fetch_results(query, value)
            composizioni_raw: list[Composizione] = [Composizione(*x) for x in rows] if rows else []
        except Exception as e:
            logger.error(f"Errore nel recupero della composizione: {e}")
            return None

        # 3. Ricorsione per ogni composizione
        for comp in composizioni_raw:
            input_lotto = self.carica_lotto_con_composizione(comp.id_lotto_input)
            composizione = Composizione(
                id_lotto_input=comp.id_lotto_input,
                quantita_utilizzata=comp.quantita_utilizzata,
                lotto_input=input_lotto
            )
            lotto.composizione.append(composizione)

        return lotto
    

    def get_lista_prodotti(self):

        query,value = (
            self.query_builder.select(
                "Prodotto.nome",
                "Operazione.Id_lotto",
                "Azienda.nome",
                "Operazione.Id_prodotto",
            )
            .table("Operazione")
            .join("Azienda", "Operazione.Id_azienda", "Azienda.Id_azienda")
            .join("Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto")
            .where("Operazione.Tipo", "=", db_default_string.TIPO_OP_VENDITA)
            .get_query()
        )
        
        try:
            # Esegui direttamente il raw SQL (non serve builder qui)
            results = self.db.fetch_results(query, value)
            if results:
                prodotti_co2 = [ProdottoFinito(*r) for r in results]
            
                return prodotti_co2
            else:
                logger.warning("Nessun risultato trovato ")
                return []
        except Exception as e:
            logger.error(f"Errore in calcola_co2_totale_per_prodotti_finiti: {e}")
            return []
    