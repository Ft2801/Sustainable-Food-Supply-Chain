# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from abc import ABC
import sqlite3
from typing import Union
from domain.exception.database_exceptions import UniqueConstraintError
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.exception.login_exceptions import HaveToWaitException, ToManyTryLogEXcepition
from persistence.query_builder import QueryBuilder
from model.credential_model import UserModel
from model.company_model import CompanyModel
from persistence.repository_impl.database_standard import aziende_enum
from session import Session

"""
class "CredentialRepositoryImpl(CredentialRepository, ABC)"
    Defines the "CredentialRepositoryImpl" class, which inherits from CredentialRepository 
    and ABC (Abstract Base Class).
    ABC indicates that the class can contain abstract methods and is part of a design pattern
    "Repository" based on abstract classes.
"""


class CredentialRepositoryImpl(ABC):
  
    def __init__(self):
        self.db = Database()
        self.query_builder = QueryBuilder()
        logger.info("BackEnd: Successfully initializing the instance for CredentialRepositoryImpl.")

    def get_user(self, user: str) -> Union[UserModel, None]:
        try:
            query,value = ( 
                self.query_builder.select("*").table("Credenziali").where("Username", "=",user).get_query())
            logger.info(f"{self.db.fetch_results(query,value)}")    
            return UserModel(*self.db.fetch_results(query,value)[0])
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali nel rep: {str(e)}")
            return None


    def get_lista_credenziali(self) -> list[UserModel]:
        try:

            query,value = ( 
                self.query_builder.select("*").table("credenziali").get_query())


            result = [UserModel(*x) for x in self.db.fetch_results(query,value) ]
            
            
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali nel rep: {str(e)}")
            return []
        
    
        if not result:
            logger.warning("The credenziali table is empty or the query returned no results.")
        else:
            logger.info(f"Credenziali obtained ")

        return result

    def get_azienda_by_id(self, id: int) -> CompanyModel:
        query, value = (
            self.query_builder.select("*").table("Azienda").where("Id_azienda","=",id).get_query()
        )

        try:
            result = self.db.fetch_results(query, value)
            return CompanyModel(*self.db.fetch_results(query, value)[0])
            
        except Exception as e:
            logger.info(f" Errore nel repository{e} ")
            return False


    def register(self, username: str, password: str, tipo: aziende_enum, indirizzo: str):
        try:
            UserModel.validate_password(password)
            hash_password = UserModel.hash_password(password= password)
            self.db.cur.execute("BEGIN TRANSACTION;")  # Inizio transazione manuale
            # Prima INSERT: credenziali
            query_credenziali = """
                INSERT INTO Credenziali (Username, Password)
                VALUES (?, ?);
            """
            self.db.cur.execute(query_credenziali, (username, hash_password))
            logger.info(f"Inserisco le credenziali del nuovo utente {username}")
            id_credenziali = self.db.cur.lastrowid  # Ottieni l'ID appena creato
            # Seconda INSERT: azienda
            query_azienda = """
                INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
                VALUES (?, ?, ?, ?);
            """
            self.db.cur.execute(query_azienda, (id_credenziali, tipo, username, indirizzo))
            logger.info(f"Inserisco le informazione dell'azienda collegata all'utente {username}")

            self.db.conn.commit()  # Commit manuale dell'intera transazione
            return id_credenziali

        except sqlite3.IntegrityError:
            self.db.conn.rollback()  # Rollback su vincolo violato
            logger.error(f"Errore: Username già esistente.")
            raise UniqueConstraintError("Errore: Username già esistente.")

        except Exception as e:
            self.db.conn.rollback()
            logger.error(f"Errore durante l'inserimento delle credenziali e dell'azienda: {str(e)}")
            raise e

    def verifica_password(self,old_psw,user_id: str) -> bool:
        try:
            query = "SELECT Password FROM Credenziali WHERE Id_credenziali = ?"
            if Session().current_user["id_azienda"] == user_id:
                param = (user_id,)
                db_psw : str = self.db.fetch_one(query,param)
            else:
                raise Exception("Controllo username fallito")
            
            hash_old = UserModel.hash_password(old_psw)

            if hash_old == db_psw:
                return True
            else:
                return False

        except Exception as e:
            raise Exception("Errore nella verifica delle password")
        

    def cambia_password(self,new_password: str, user_id: str):
        try:
            UserModel.validate_password(new_password)
            hash_password = UserModel.hash_password(new_password)

            query = "UPDATE Credenziali SET password = ? WHERE Id_credenziali = ?"

            if Session().current_user["id_azienda"] == user_id:
                params = (hash_password,user_id)
                self.db.execute_query(query,params)
            else:
                raise Exception("Controllo username fallito")
            

            
        except HaveToWaitException as e:  
                raise e
        except  ToManyTryLogEXcepition as e:
                raise e
        except Exception as e:
            raise Exception(f"Errore nel cambio della password {e}")