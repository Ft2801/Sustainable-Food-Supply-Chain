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
                self.query_builder.select("Id_credenziali","Username","Password" )
                .table("Credenziali").where("Username", "=",user).get_query())    
            results = self.db.fetch_results(query,value)
            
            # Verifica se ci sono risultati prima di tentare di accedere all'elemento [0]
            if results and len(results) > 0:
                return UserModel(*results[0])
            else:
                logger.warning(f"Nessun utente trovato con username: {user}")
                return None
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali nel rep: {str(e)}")
            return None



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
                INSERT INTO Credenziali (Username, Password, address)
                VALUES (?, ?, ?);
            """
            address = indirizzo #TODO  Cambiare con l'indirizzo
            self.db.cur.execute(query_credenziali, (username, hash_password,address))
            logger.info(f"Inserisco le credenziali del nuovo utente {username}")
            id_credenziali = self.db.cur.lastrowid  # Ottieni l'ID appena creato
            
            # Seconda INSERT: azienda
            query_azienda = """
                INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
                VALUES (?, ?, ?, ?);
            """
            self.db.cur.execute(query_azienda, (id_credenziali, tipo, username, indirizzo))
            logger.info(f"Inserisco le informazione dell'azienda collegata all'utente {username}")

            # Commit manuale dell'intera transazione
            self.db.conn.commit()
            
            # Ottieni l'ID dell'azienda appena creata
            query_id_azienda = "SELECT Id_azienda FROM Azienda WHERE Id_credenziali = ?"
            self.db.cur.execute(query_id_azienda, (id_credenziali,))
            id_azienda = self.db.cur.fetchone()[0]
            
            # Registra l'azienda sulla blockchain
            try:
                from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl
                richieste_repo = RichiesteRepositoryImpl()
                blockchain_registration = richieste_repo.register_company_on_blockchain(id_azienda)
                if blockchain_registration:
                    logger.info(f"Azienda {username} registrata con successo sulla blockchain")
                else:
                    logger.warning(f"Impossibile registrare l'azienda {username} sulla blockchain. Sarà registrata in seguito.")
            except Exception as e:
                logger.warning(f"Errore durante la registrazione dell'azienda sulla blockchain: {str(e)}. L'azienda sarà registrata in seguito.")
            
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
        

    def get_adrress_by_id(self, id: int) -> str:
        try:
            query = "SELECT address FROM Credenziali WHERE Id_credenziali = ?"
            value = (id,)
            result = self.db.fetch_results(query, value)
            if result:
                return result[0][0]
            else:
                raise Exception("Nessun indirizzo trovato per l'ID fornito.")
        except Exception as e:
            logger.error(f"Errore durante il recupero dell'indirizzo: {str(e)}")
            raise e