# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import datetime
from abc import ABC
import sqlite3
from typing import Final
from pydantic import BaseModel
import hmac
import hashlib
import os
from configuration.database import Database
from configuration.log_load_setting import logger
from model.operation_model import OperationModel
from model.operation_estesa_model import OperazioneEstesaModel
from model.prodotto_finito_model import ProdottoLottoModel
from persistence.query_builder import QueryBuilder

from persistence.repository_impl import db_default_string


class FirmaRequest(BaseModel):
    tipo_operazione: str
    id_prodotto: int
    soglia_massima: int

class VerificaRequest(FirmaRequest):
    signature: str


SECRET_KEY = os.getenv("_KEY", "default_dev_key")

class OperationRepositoryImpl(ABC):
    # Class variable that stores the single instance

    QUERY_UPDATE_AZIENDA : Final = """
                            UPDATE Azienda  
                            SET Co2_emessa = Co2_emessa + ?, Token = Token + ?  
                            WHERE Id_azienda = ?;
                        """
    

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
        

    def get_operazioni_by_azienda(self, azienda: int) -> list[OperazioneEstesaModel]:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda """

        # Utilizziamo una query senza la colonna descrizione per sicurezza
        query, value = (
            self.query_builder
                .select(
                    "Operazione.Id_operazione",
                    "Prodotto.Id_prodotto",
                    "Prodotto.Nome",
                    "Operazione.Data_operazione",
                    "Operazione.Consumo_CO2",
                    "Operazione.Tipo",
                    "Operazione.quantita",
                    "Operazione.blockchain_registered",
                    "Operazione.Id_lotto"
                )
                .table("Operazione")
                .join("Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto")
                .where("Operazione.Id_azienda", "=", azienda)
                .get_query()
        )

        try:
            results = self.db.fetch_results(query, value)
            if results is None:
                logger.error("No results returned from database")
                return []
                
            operazioni_estese = []
            for row in results:
                try:
                    operazione = OperazioneEstesaModel(
                        id_operazione=row[0],
                        id_lotto= row[8],  # Assuming id_lotto is the second column
                        id_prodotto=row[1],
                        nome_prodotto=row[2],
                        data_operazione=row[3],
                        consumo_co2=row[4],
                        nome_operazione=row[5],
                        quantita_prodotto=row[6],
                        blockchain_registered=bool(row[7]) if len(row) > 7 else False
                    )
                    operazioni_estese.append(operazione)
                except Exception as e:
                    logger.error(f"Error creating OperazioneEstesaModel: {e} for row: {row}", exc_info=True)
            
            return operazioni_estese   
        except Exception as e:
            logger.error(f"Error fetching operations by company: {e}", exc_info=True)
            return []
    



    def inserisci_operazione_azienda_rivenditore(self, azienda: int, prodotto: int, data: datetime, co2: int,
                                                 evento: str, id_lotto_input: int, quantita : int):
        """
        Inserts a new operation for a retailer and updates the product status in a single transaction.
        """
        try:
            
            queries=[]

            
            value_output_lotto = self.get_next_id_lotto_output()
            query = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
            params = (value_output_lotto,id_lotto_input,quantita)

            queries.append((query, params))
            
            query = """
                INSERT INTO Operazione (Id_azienda, Id_prodotto,Id_lotto, Data_operazione, Consumo_CO2, Tipo,quantita)
                VALUES (?, ?, ?, ?, ?,?,?);
            """
            params = (azienda, prodotto,value_output_lotto, data, co2, evento,quantita)

            queries.append((query, params))

            

            # Aggiornare Magazzino
            query = "UPDATE Magazzino SET quantita = quantita - ? WHERE Id_azienda = ? AND Id_lotto = ?"
            params = (quantita,azienda,id_lotto_input)

            queries.append((query, params))

            # Registrazione del consumo CO2 (senza assegnazione token)
            # I token verranno assegnati solo quando l'operazione sarà registrata sulla blockchain
            query = "UPDATE Azienda SET Co2_emessa = Co2_emessa + ? WHERE Id_azienda = ?"
            params = (co2, azienda)
            queries.append((query, params))

            self.db.execute_transaction(queries)

        
        except Exception as e:
            raise Exception(f"BackEnd: inserisci_operazione_azienda_rivenditore: Error inserting retailer operation: {str(e)}")


    """ Funzionanti"""

    def inserisci_operazione_azienda_agricola(self, id_tipo_prodotto: int, descrizione : str, quantita: int, azienda: int, data: datetime, co2: int):
        """
        Inserts a new agricultural product and logs the operation.
        """
        try:

            queries = []

            tipo_evento = db_default_string.TIPO_OP_PRODUZIONE
            id_lotto = self.get_next_id_lotto_output()
            query, value = (
                self.query_builder.table("Operazione")
                .insert(Id_azienda=azienda, Id_prodotto=id_tipo_prodotto, Data_operazione=data, Consumo_CO2=co2,
                        Tipo=tipo_evento, Id_lotto= id_lotto, quantita=quantita)
                .get_query()
            )

            queries.append((query,value))
            

            query, value = (
                self.query_builder.table("Magazzino")
                .insert(Id_azienda=azienda, id_lotto=id_lotto, quantita=quantita)
                .get_query()
            )

            queries.append((query,value))

            # Registrazione del consumo CO2 (senza assegnazione token)
            # I token verranno assegnati solo quando l'operazione sarà registrata sulla blockchain
            query = "UPDATE Azienda SET Co2_emessa = Co2_emessa + ? WHERE Id_azienda = ?"
            params = (co2, azienda)
            queries.append((query, params))

            self.db.execute_transaction(queries)

            logger.info(f"Operazione registrata con successo.")
        except Exception as e:
            logger.error(f"Errore durante l'inserimento del prodotto: {str(e)}")
            raise Exception(f"Errore nell'inserimento: {e}")


    def inserisci_operazione_trasporto(self, id_azienda_trasporto: int,id_lotto_input: int, id_prodotto: int, id_azienda_richiedente: int, id_azienda_ricevente: int, quantita: int, co2_emessa: int):
        """
        Inserts a new transport operation and updates the product status.
        """
        try:

            evento = db_default_string.TIPO_OP_TRASPORTO

            queries = []


            query = "SELECT quantita FROM Magazzino WHERE id_lotto = ?"
            params = (id_lotto_input,)

            quantita_disponibile = self.db.fetch_one(query,params)

            if quantita_disponibile is None:
                raise Exception(f"{id_lotto_input} non trovato") 

            if quantita_disponibile < quantita:
                raise Exception( f"Quantità insufficiente: disponibile {quantita_disponibile}, richiesta {quantita}.")
            
            #vendita
            value_output_lotto = self.get_next_id_lotto_output()

            query = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
            params = (value_output_lotto, id_lotto_input, quantita)  

            queries.append((query,params))
            
       

            query = "INSERT INTO Operazione (Id_azienda,Id_prodotto,Id_lotto, Quantita, Consumo_CO2, tipo) VALUES (?, ?, ?, ?, ?, ?)"
            params = (id_azienda_trasporto,id_prodotto, value_output_lotto, quantita, 0,db_default_string.TIPO_OP_VENDITA)

            queries.append((query,params))


            #Trasporto
            lotto_vendita : int = value_output_lotto + 1
            query = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
            params = (lotto_vendita, value_output_lotto, quantita)  

            queries.append((query,params))
            
       

            query = "INSERT INTO Operazione (Id_azienda,Id_prodotto,Id_lotto, Quantita, Consumo_CO2, tipo) VALUES (?, ?, ?, ?, ?, ?)"
            params = (id_azienda_ricevente,id_prodotto, lotto_vendita, quantita, co2_emessa,evento)

            queries.append((query,params))

            

        
            # Aggiornamento del magazzino
            query = "INSERT INTO Magazzino(id_azienda,id_lotto,quantita) VALUES(?,?,?)"
            params = (id_azienda_richiedente,lotto_vendita,quantita)

            queries.append((query,params))

            
            query_mag = """UPDATE Magazzino SET quantita = quantita - ? WHERE id_lotto = ?;""" 
            value_mag = (quantita, id_lotto_input)
            queries.append((query_mag, value_mag))

            
            # Registrazione del consumo CO2 (senza assegnazione token)
            # I token verranno assegnati solo quando l'operazione sarà registrata sulla blockchain
            query = "UPDATE Azienda SET Co2_emessa = Co2_emessa + ? WHERE Id_azienda = ?"
            params = (co2_emessa, id_azienda_trasporto)
            queries.append((query, params))



            self.db.execute_transaction(queries)

            logger.info(f"Operazione di trasporto inserita con successo.")


            logger.info( f"Aggiornamento riuscito: {quantita} sottratti dal lotto {id_lotto_input}.")

        except Exception as e:
            logger.error(f"Errore durante l'inserimento dell'operazione di trasporto: {str(e)}")
            raise Exception(f"Errore nel inserimento: {e}")


    def inserisci_prodotto_trasformato(self, id_tipo_prodotto: int, descrizione: str, quantita_prodotta: int, materie_prime_usate: dict, id_azienda: int, co2_consumata: int):
        """
        Salva un prodotto trasformato nel database con le materie prime utilizzate.
        
        :param nome_prodotto: Nome del prodotto trasformato
        :param quantita_prodotta: Quantità del prodotto trasformato
        :param materie_prime_usate: dict con chiave qualsiasi e valore (ProdottoLottoModel, quantita_usata)
        """

        try:
            queries = []
            tipo_evento = "trasformazione"

            # 1. Ottieni il prossimo ID lotto output
            value_output_lotto = self.get_next_id_lotto_output()
            
            # 2. IMPORTANTE: Inserisci PRIMA l'operazione di trasformazione
            # Questo è necessario per soddisfare il vincolo di chiave esterna in ComposizioneLotto
            query_operazione = "INSERT INTO Operazione (Id_azienda,\
                  Id_prodotto , Id_lotto ,Consumo_CO2 , quantita ,Tipo) VALUES (?,?,?,?,?,?)"
            value_op = (id_azienda,id_tipo_prodotto,value_output_lotto,co2_consumata,quantita_prodotta,tipo_evento)
            
            # Aggiungi l'operazione come PRIMA query da eseguire
            queries.append((query_operazione, value_op))
            
            # 3. Aggiungi nuovo lotto al magazzino
            query_magazzino = "INSERT INTO Magazzino (id_azienda, id_lotto, quantita) VALUES (?, ?, ?)"
            value = (id_azienda, value_output_lotto, quantita_prodotta)
            queries.append((query_magazzino, value))
            
            # 4. Prepara update quantità materie prime
            for _, (materia, quantita_usata) in materie_prime_usate.items():
                if isinstance(materia, ProdottoLottoModel):
                    print(f"\n\\nn\n\nn\n\n\n\n\n\n\ {quantita_usata}\n\n\n\n\n")
                    query_update_materia ="UPDATE Magazzino SET quantita = quantita - ? WHERE id_lotto = ?"
                    value = (quantita_usata,materia.id_lotto)
                    queries.append((query_update_materia, value))
            
            # 5. Ora crea le composizioni del lotto (dopo aver creato l'operazione)
            for _, (materia, quantita_usata) in materie_prime_usate.items():
                if isinstance(materia, ProdottoLottoModel):
                    query_comp = "INSERT INTO ComposizioneLotto (id_lotto_output, id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
                    params = (value_output_lotto, materia.id_lotto, quantita_usata)
                    queries.append((query_comp, params))

            # 6. Aggiorna solo la CO2 dell'azienda (senza assegnazione token)
            # I token verranno assegnati solo quando l'operazione sarà registrata sulla blockchain
            query = "UPDATE Azienda SET Co2_emessa = Co2_emessa + ? WHERE Id_azienda = ?"
            params = (co2_consumata, id_azienda)
            queries.append((query, params))
            
            # 7. Esegui la transazione
            self.db.execute_transaction(queries)

            return self.recupera_soglia(tipo_evento, id_tipo_prodotto)

        except sqlite3.IntegrityError as e:
            print("IntegrityError:", e)
            self.db.conn.rollback()

        except Exception as e:
            # Se c'è un errore, rollback dell'intera transazione
            self.db.conn.rollback()
            raise Exception(f"Errore durante la creazione del prodotto trasformato: {e}")
         

    def get_next_id_lotto_output(self):
        try:
            # Ottieni il massimo ID lotto dalla tabella ComposizioneLotto
            max_composizione = self.db.fetch_one("SELECT IFNULL(MAX(id_lotto_output), 0) FROM ComposizioneLotto;")
            
            # Ottieni il massimo ID lotto dalla tabella Operazione
            max_operazione = self.db.fetch_one("SELECT IFNULL(MAX(Id_lotto), 0) FROM Operazione;")
            
            # Usa il massimo tra i due valori e aggiungi 1
            max_id = max(max_composizione or 0, max_operazione or 0)
            value_output_lotto = max_id + 1
            
            return value_output_lotto
        except Exception as e:
            logger.error(f"Errore nell'ottenimento del nuovo id lotto: {str(e)}")
            raise ValueError(f"Errore nell'ottenimento del nuovo id lotto: {str(e)}")

    def token_opeazione(self,co2_consumata :int,tipo_operazione: str, id_prodotto: int) -> int:
        try:
            return  self.recupera_soglia(tipo_operazione, id_prodotto) - co2_consumata
        except Exception as e:
            logger.error(f"Errore nel calcolo dei token {e}")
            return 0
        

    def recupera_soglia(self, tipo_operazione: str, id_prodotto: int) ->int:
        result = self.db.fetch_results("""
            SELECT Operazione, Prodotto, Soglia_Massima, firma FROM Soglie WHERE Operazione = ? AND Prodotto = ?
        """, (tipo_operazione, id_prodotto))

        if not result:
            raise ValueError("Soglia non trovata.")
        

        tipo_operazione, id_prodotto, soglia_massima, firma = result[0]
        
        # Assicurati che i tipi siano coerenti con quelli usati nella firma originale
        payload : dict = {
            "tipo_operazione": tipo_operazione,
            "id_prodotto": id_prodotto,
            "soglia_massima": soglia_massima,
    
        }

        logger.info(f"{firma}")

        if not self.verifica_dati(payload,firma):
            raise ValueError("Dati soglia corrotti o manomessi!")

        return soglia_massima
        

    def verifica_dati(self,payload : dict,signature : str):
        raw_string = f"{payload['tipo_operazione']}|{payload['id_prodotto']}|{payload['soglia_massima']}"
        expected_signature = hmac.new(SECRET_KEY.encode(), raw_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            return False
        
        return True
    


    
            


         