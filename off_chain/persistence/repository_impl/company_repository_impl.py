# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from model.company_model import CompanyModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl.database_standard import *
from persistence.repository_impl import db_default_string 


class CompanyRepositoryImpl(ABC):
    """
     Implementing the aziende repository.
     """

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()


    def get_aziende_trasporto(self) -> list[CompanyModel]:
        """
        Get all the transport companies from the database.
        """
        self.query_builder.select("*").table("Azienda").where("Tipo", "=", "Trasportatore")
        query, value = (self.query_builder.get_query())
        result = self.db.fetch_results(query, value)
        try:
            return [CompanyModel(*x) for x in result]
        except Exception as e:
            print(e)
            return []
        

    def get_lista_aziende(self, tipo: aziende_enum = None, 
                          nome : str = None, id : int = None, escludi_azienda : int = None) -> list[CompanyModel]:
        
        self.query_builder.select("*").table("Azienda")


        if not tipo: 
                self.query_builder.where("Tipo", "!=" , db_default_string.TIPO_AZIENDA_TRASPORTATORE)

        if nome:
            self.query_builder.where("Nome", "=",nome)

        if id:
            self.query_builder.where("Id_azienda", "=",id)
        if escludi_azienda:
            self.query_builder.where("Id_azienda", "!=", escludi_azienda)
            

        query, value= (self.query_builder.get_query())
        result = self.db.fetch_results(query,value)
        try:
            print(result[0])
            return [CompanyModel(*x) for x in result]
        
        except Exception as e:
            print(e)
            return []
            


    def get_azienda(self, n: int) -> CompanyModel:
        return self.get_lista_aziende()[n]
