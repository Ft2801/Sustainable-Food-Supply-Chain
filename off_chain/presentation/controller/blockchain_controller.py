from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import json
import os
import sqlite3
from session import Session
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl
from persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl
from persistence.repository_impl import db_default_string
from configuration.log_load_setting import logger
import subprocess
import requests
import time
from configuration.database import Database

# CONFIGURAZIONE
NODE_URL = "http://127.0.0.1:8545"  # Nodo Hardhat

# Ottieni il percorso assoluto alla directory del progetto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# Usa percorsi assoluti per i file di configurazione
# Percorso diretto all'ABI del contratto negli artifacts
ABI_PATH = os.path.join(PROJECT_ROOT, "on_chain", "artifacts", "contracts", "SustainableFoodChain.sol", "SustainableFoodChain.json")
ADDRESS_PATH = os.path.join(PROJECT_ROOT, "on_chain", "contract_address.json")
# Definizione diretta del percorso del database
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'off_chain', 'database', 'database.db')

# Web3 setup
w3 = Web3(Web3.HTTPProvider(NODE_URL))

class BlockchainController:
    def __init__(self):
        self.controller = CredentialRepositoryImpl()
        self.richieste_controller = RichiesteRepositoryImpl()
        with open(ABI_PATH) as f:
            contract_json = json.load(f)
            abi = contract_json["abi"]

        with open(ADDRESS_PATH) as f:
            address_json = json.load(f)
            contract_address = address_json.get("SustainableFoodChain")
            if not contract_address:
                raise ValueError("Indirizzo del contratto non trovato nel file contract_address.json sotto la chiave 'SustainableFoodChain'.")

        self.contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)

    @staticmethod
    def verifica_possesso_chiave(address_eth, signature, challenge):
        message = encode_defunct(text=challenge)
        recovered = Account.recover_message(message, signature=signature)
        return recovered.lower() == address_eth.lower()
    
    

    def firma_operazione(self,tipo, id_lotto, id_operazione):

        account = self.get_address()  # Funzione che recupera account locale

        messaggio = f"Conferma operazione {tipo} lotto {id_lotto} con id op {id_operazione}"
        messaggio_encoded = messaggio.replace(" ", "%20")

        url = f"http://localhost:5001/firma_operazione.html?messaggio={messaggio_encoded}&tipo={tipo}&lotto={id_lotto}&op={id_operazione}"
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                proc = subprocess.Popen([chrome_path, url])
                proc.wait()
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            raise Exception(f"Errore nell'apertura del browser: {str(e)}")
        
        max_wait = 10  # secondi
        wait_interval = 2  # secondi
        start_time = time.time()

        while time.time() - start_time < max_wait:

            try:
                print(f"Attendo esito operazione {id_operazione} per l'account {account}")
                response = requests.get(f"http://localhost:5001/esito_operazione/{account}/{id_operazione}", timeout=10)
                data = response.json()
                if "esito" in data:
                    esito = data["esito"]
                    logger.info(f"Esito  {esito}")
                    return esito
            except requests.RequestException:
                pass  # Continua a riprovare

            time.sleep(wait_interval)

        raise TimeoutError("Timeout in attesa della firma tramite MetaMask")


    def firma_azione_compensativa(self, tipo, id_azione, co2_compensata):
        """
        Gestisce la firma di un'azione compensativa tramite MetaMask.
        
        Args:
            tipo: Il tipo di azione compensativa (es. 'Piantumazione', 'Energia rinnovabile')
            id_azione: L'ID dell'azione compensativa
            co2_compensata: La quantità di CO2 compensata dall'azione
        
        Returns:
            str: L'esito dell'operazione
        """
        account = self.get_address()  # Funzione che recupera account locale

        # Crea un messaggio descrittivo per l'azione compensativa
        messaggio = f"Conferma azione compensativa '{tipo}' con ID {id_azione} e CO2 compensata {co2_compensata}"
        messaggio_encoded = messaggio.replace(" ", "%20")

        # Costruisci l'URL con tutti i parametri necessari
        url = f"http://localhost:5001/firma_azione_compensativa.html?messaggio={messaggio_encoded}&tipo={tipo}&id_azione={id_azione}&co2_compensata={co2_compensata}"
        
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                proc = subprocess.Popen([chrome_path, url])
                proc.wait()
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            raise Exception(f"Errore nell'apertura del browser: {str(e)}")
        
        # Attendi la risposta dal servizio web
        max_wait = 60  # secondi
        wait_interval = 3  # secondi
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                print(f"Attendo esito azione compensativa {id_azione} per l'account {account}")
                response = requests.get(f"http://localhost:5001/esito_azione_compensativa/{account}/{id_azione}", timeout=10)
                data = response.json()
                if "esito" in data:
                    esito = data["esito"]
                    logger.info(f"Esito azione compensativa: {esito}")
                    return esito
            except requests.RequestException as e:
                print(f"Errore nella richiesta HTTP: {e}")
                pass  # Continua a riprovare

            time.sleep(wait_interval)

        raise TimeoutError("Timeout in attesa della firma tramite MetaMask")


    def get_address(self):
        try:
            session = Session()
            current_user = getattr(session, "current_user", None)
            if current_user is None:
                raise ValueError("Utente non autenticato (current_user è None)")

            if not isinstance(current_user, dict):
                raise TypeError(f"current_user non è un dizionario: {type(current_user)}")

            if "id_azienda" not in current_user:
                raise ValueError("Chiave 'id_azienda' mancante in current_user")

            return self.controller.get_address_by_id(current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nel recupero dell'indirizzo dell'utente: {e}")
            raise


    def invia_azione(self, tipo_azione, description, data_azione, co2_compensata, account_address):
        """Registra un'azione compensativa sulla blockchain"""
        try:
            # Debugging dei tipi di dati ricevuti
            logger.info(f"DATI RICEVUTI - tipo_azione: {tipo_azione} (tipo: {type(tipo_azione)}), "
                        f"description: {description} (tipo: {type(description)}), "
                        f"data_azione: {data_azione} (tipo: {type(data_azione)}), "
                        f"co2_compensata: {co2_compensata} (tipo: {type(co2_compensata)})")
            
            # Ottieni l'account dall'indirizzo blockchain dell'utente corrente
            account = Web3.to_checksum_address(account_address)
            nonce = w3.eth.get_transaction_count(account)
            gas_price = w3.eth.gas_price
            
            # Assicurati che i tipi di dati siano corretti per il contratto
            # Converti i tipi se necessario - usa try/except per gestire casi di stringa
            try:
                co2_compensata_int = int(co2_compensata)  # Converti in intero per uint8
            except (ValueError, TypeError):
                logger.warning(f"Impossibile convertire co2_compensata a intero: {co2_compensata}, impostando a 0")
                co2_compensata_int = 0
                
            logger.info(f"Invio azione: tipo={tipo_azione}, desc={description}, data={data_azione}, co2={co2_compensata_int}")
            
            # Il contratto registerCompensationAction accetta solo 3 parametri, non 4
            # L'identificazione dell'azienda avviene tramite msg.sender nel contratto
            tx = self.contract.functions.registerCompensationAction(
                tipo_azione,
                co2_compensata_int,
                description
            ).build_transaction({
                'from': account,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': 300000,
            })

            # Firma e invia la transazione
            tx_hash = w3.eth.send_transaction(tx)
            
            # Aggiorna lo stato dell'azione compensativa nel database
            try:
                # Estrai l'ID dell'azione dalla descrizione se possibile
                id_azione_match = None
                if isinstance(description, str) and "ID" in description:
                    import re
                    id_match = re.search(r'ID\s+(\d+)', description)
                    if id_match:
                        id_azione_match = id_match.group(1)
                        logger.info(f"Estratto ID azione {id_azione_match} dalla descrizione")
                
                # Usa l'ID estratto o cerca nei parametri locali
                id_azione_param = id_azione_match
                if not id_azione_param and 'id_azione' in locals():
                    id_azione_param = id_azione
                
                if id_azione_param:
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    
                    # Verifica se l'azione esiste prima di aggiornare
                    cursor.execute(
                        "SELECT COUNT(*) FROM Azioni_compensative WHERE Id_azione = ?",
                        (id_azione_param,)
                    )
                    if cursor.fetchone()[0] > 0:
                        # Aggiorna il flag blockchain_registered
                        cursor.execute(
                            "UPDATE Azioni_compensative SET blockchain_registered = 1 WHERE Id_azione = ?",
                            (id_azione_param,)
                        )
                        conn.commit()
                        logger.info(f"Azione compensativa {id_azione_param} marcata come registrata sulla blockchain")
                    else:
                        logger.warning(f"Azione compensativa con ID {id_azione_param} non trovata nel database")
                    
                    conn.close()
                else:
                    logger.warning("Impossibile aggiornare lo stato dell'azione compensativa: ID azione non disponibile")
            except Exception as e:
                logger.error(f"Errore nell'aggiornamento dello stato dell'azione compensativa: {e}")
                # Non solleviamo l'eccezione qui per non interrompere il flusso principale
            
            return tx_hash.hex()
        
        except Exception as e:
            logger.error(f"Errore durante l'invio dell'operazione sulla blockchain: {e}")
            raise Exception(f"Errore durante l'invio dell'operazione sulla blockchain: {str(e)}")

    def invia_operazione(self, operation_type, description, batch_id, id_operazione, account_address):
        """Registra un'operazione sulla blockchain"""
        try:
            # Log dei parametri di input con formato strutturato
            logger.info(f"[Operazione #{id_operazione}] Parametri: tipo={operation_type}, lotto={batch_id}, descrizione='{description}'")
            
            # Recupero informazioni sui lotti di input dal database
            db = Database()
            query = "SELECT id_lotto_input, quantità_utilizzata FROM ComposizioneLotto WHERE id_lotto_output = ? "
            params = (batch_id,)
            result = db.fetch_results(query=query, params=params)
            
            # Estrazione dei dati dai risultati della query
            id_lotti = [row[0] for row in result] if result else []
            quantita_lotti = [row[1] for row in result] if result else []
            
            # Log dei lotti di input con formato strutturato
            if id_lotti:
                logger.info(f"[Operazione #{id_operazione}] Composizione: lotto {batch_id} composto da {len(id_lotti)} lotti di input")
                for i, (lotto_id, quantita) in enumerate(zip(id_lotti, quantita_lotti)):
                    logger.info(f"  - Input #{i+1}: lotto {lotto_id}, quantità {quantita}")
            else:
                logger.info(f"[Operazione #{id_operazione}] Nessun lotto di input (operazione di produzione primaria)")

            query_op = "SELECT Id_prodotto, Consumo_CO2, quantita FROM Operazione WHERE Id_operazione = ? "
            params = (id_operazione,)
            result = db.fetch_results(query=query_op,params=params)

            if result:
                id_prodotto, co2Consumed_db, quantita_db = result[0]
                
            else:
                raise Exception("Errore nel'inserimento dell'operazione")
            
            try:
                co2Consumed = int(co2Consumed_db)
                quantita = int(quantita_db)
            except ValueError as e:
                raise ValueError(f"co2 o quantita non interi")


            operation_type_map = {
                "produzione": 0,
                "trasformazione": 1,
                "distribuzione": 2,
                "vendita": 3
            }
            tipo_bc = operation_type_map.get(operation_type, 0)

            if operation_type != db_default_string.TIPO_OP_VENDITA:

                query = """
                SELECT c.Address
                FROM Magazzino AS m
                JOIN Azienda AS a ON m.id_azienda = a.Id_azienda
                JOIN Credenziali AS c ON a.Id_credenziali = c.Id_credenziali
                WHERE m.id_lotto = ?
                """
                params = (batch_id,)
                account_lotto = db.fetch_results(query=query, params=params)

                logger.info(f"account destinazione lotto: {account_lotto}")
                
                azienda_proprietaria_lotto = Web3.to_checksum_address(account_lotto[0][0]) 
            else:
                azienda_proprietaria_lotto =  Web3.to_checksum_address('0x0000000000000000000000000000000000000000')



            
            rep = OperationRepositoryImpl()
            soglia_op = rep.recupera_soglia(operation_type,id_prodotto)
            logger.info(f"soglia_recuperata = {soglia_op}")


            
            # Verifica e gestisci tipi di dati anomali
            if isinstance(operation_type, list):
                logger.warning(f"operation_type è una lista: {operation_type}, usando il primo elemento o 0")
                operation_type = operation_type[0] if operation_type else 0
            
            if isinstance(batch_id, list):
                logger.warning(f"batch_id è una lista: {batch_id}, usando il primo elemento o 1")
                batch_id = batch_id[0] if batch_id else 1
                
            # Ottieni l'account dall'indirizzo blockchain dell'utente corrente
            account = Web3.to_checksum_address(account_address)
            nonce = w3.eth.get_transaction_count(account)
            gas_price = w3.eth.gas_price

            
            # Converti i tipi se necessario - usa try/except per gestire casi di stringa
            try:
                operation_type_int = int(tipo_bc)  # Converti in intero per uint8
            except (ValueError, TypeError):
                logger.warning(f"Impossibile convertire operation_type a intero: {operation_type}, impostando a 0")
                operation_type_int = 0
                
            try:
                batch_id_int = int(batch_id)  # Converti in intero per uint256
            except (ValueError, TypeError):
                logger.warning(f"Impossibile convertire batch_id a intero: {batch_id}, impostando a 1")
                batch_id_int = 1


            logger.info(f"indirizzo destinaario {azienda_proprietaria_lotto}")
            
            logger.info(f"[Operazione #{id_operazione}] Preparazione transazione: lotto={batch_id_int}, tipo={operation_type_int}")

            input_struct = {
                'idOperazione': id_operazione,  # Converti esplicitamente in intero
                'operationType': operation_type_int,
                'batchId': batch_id_int,
                'quantita': quantita,  # Converti esplicitamente in intero
                'idLotti': id_lotti ,  # Converti ogni ID in intero
                'quantitaLotti': quantita_lotti,  # Converti ogni quantità in intero
                'sogliaCO2': soglia_op,  # Converti esplicitamente in intero
                'consumoCO2': co2Consumed  # Converti esplicitamente in intero
            }
            
            # 1. Registra l'operazione



            tx_register = self.contract.functions.registerOperation(
                input_struct,
                azienda_proprietaria_lotto  # Usa il valore convertito a intero
            ).build_transaction({
                'from': account,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': 650000,
            })
            
            # Invia la prima transazione
            tx_hash_register = w3.eth.send_transaction(tx_register)
            receipt_register = w3.eth.wait_for_transaction_receipt(tx_hash_register, timeout=120)
            logger.info(f"[Operazione #{id_operazione}] Transazione 1/3 (registerOperation): {tx_hash_register.hex()}, status={receipt_register.status}")
            
            """
            # Incrementa il nonce per la prossima transazione
            nonce = w3.eth.get_transaction_count(account)
            
            # 2. Crea la composizione del lotto (solo se ci sono lotti di input)
            if id_lotti and len(id_lotti) > 0:
                tx_composizione = self.contract.functions.createComposizioneLotto(
                    batch_id_int,
                    id_lotti,
                    quantita_lotti
                ).build_transaction({
                    'from': account,
                    'nonce': nonce,
                    'gasPrice': gas_price,
                    'gas': 650000,
                })
                
                # Invia la seconda transazione
                tx_hash_composizione = w3.eth.send_transaction(tx_composizione)
                receipt_composizione = w3.eth.wait_for_transaction_receipt(tx_hash_composizione, timeout=120)
                logger.info(f"[Operazione #{id_operazione}] Transazione 2/3 (createComposizioneLotto): {tx_hash_composizione.hex()}, status={receipt_composizione.status}")
                
                # Incrementa il nonce per la prossima transazione
                nonce = w3.eth.get_transaction_count(account)
            
            # 3. Assegna i token in base al consumo di CO2
            tx_token = self.contract.functions.assignTokensByConsumption(
                soglia_op,
                co2Consumed
            ).build_transaction({
                'from': account,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': 650000,
            })
            
            # Invia la terza transazione
            tx_hash_token = w3.eth.send_transaction(tx_token)
            receipt_token = w3.eth.wait_for_transaction_receipt(tx_hash_token, timeout=120)
            logger.info(f"[Operazione #{id_operazione}] Transazione 3/3 (assignTokensByConsumption): {tx_hash_token.hex()}, status={receipt_token.status}, CO2: soglia={soglia_op}, consumata={co2Consumed}")
            """
            # Usa l'hash della prima transazione come riferimento principale
            tx_hash = tx_hash_register

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
            
            # Aggiorna lo stato dell'operazione nel database
                if id_operazione is not None:
                    try:
                        conn = sqlite3.connect(DATABASE_PATH)
                        cursor = conn.cursor()
                        # Recupera i dettagli dell'operazione per calcolare i token da assegnare
                        cursor.execute(
                            """SELECT O.Id_azienda, O.Id_prodotto, O.Consumo_CO2, O.Tipo 
                            FROM Operazione O 
                            WHERE O.Id_operazione = ?""",
                            (id_operazione,)
                        )
                        op_details = cursor.fetchone()
                        
                        if op_details:
                            id_azienda, id_prodotto, co2_consumata, tipo_operazione = op_details
                            
                            op_repo = OperationRepositoryImpl()
                            token_assegnati = op_repo.token_opeazione(co2_consumata, tipo_operazione, id_prodotto)
                            
                            # Aggiorna l'operazione come registrata sulla blockchain
                            cursor.execute(
                                "UPDATE Operazione SET blockchain_registered = 1 WHERE Id_operazione = ?",
                                (id_operazione,)
                            )

                            cursor.execute(
                                    "UPDATE Azienda SET Token = Token + ? WHERE Id_azienda = ?",
                                    (token_assegnati, id_azienda)
                                )
                            logger.info(f"Database locale sincronizzato con lo stato on-chain: {token_assegnati} token")
                    except Exception as e:
                        #gestire roll back
                        pass

                    finally:
                        conn.commit()
                        conn.close()

                        
                        # Invece di aggiornare direttamente i token nel DB, assegna i token tramite il contratto
            
            return tx_hash.hex()
        
        except Exception as e:
            logger.error(f"Errore durante l'invio dell'operazione sulla blockchain: {e}")
            raise Exception(f"Errore durante l'invio dell'operazione sulla blockchain: {str(e)}")
            
    def get_operazioni_company(self):
        try:
            address = self.get_address()
            checksum_address = Web3.to_checksum_address(address)
            res = self.contract.functions.getCompanyOperations(checksum_address).call()
            logger.info(f"Operazioni recuperate per l'azienda {address}: {res}")
            return res
        except Exception as e:
            logger.error(f"Errore nel recupero delle operazioni per {address}: {e}")
            raise Exception(f"Errore durante il recupero delle operazioni: {str(e)}")
        

    def get_all_op(self):
        try:
            res = self.contract.functions.getAllOperations().call()
            logger.info(f"Operazioni recuperate per l'azienda : {res}")
            return res
        except Exception as e:
            logger.error(f"Errore nel recupero delle operazioni per : {e}")
            raise Exception(f"Errore durante il recupero delle operazioni: {str(e)}")
        
    def getComposizione(self, id_lotto):
        """
        Recupera la catena completa di lotti e creatori per un lotto specifico.
        
        Args:
            id_lotto: ID del lotto di cui recuperare la catena
            
        Returns:
            tuple: (ids[], creatori[]) - Array di ID lotti e relativi creatori nella catena
        """
        try:
            logger.info(f"[Lotto #{id_lotto}] Recupero catena di tracciabilità")
            # getCatenaConCreatori restituisce una tupla (ids[], creatori[])
            ids, creatori = self.contract.functions.getCatenaConCreatori(id_lotto).call()
            
            # Log dettagliato della catena di lotti
            if ids and len(ids) > 0:
                logger.info(f"[Lotto #{id_lotto}] Catena di tracciabilità: trovati {len(ids)} lotti nella catena")
                for i, (lotto_id, creatore) in enumerate(zip(ids, creatori)):
                    logger.info(f"  - Anello #{i+1}: lotto {lotto_id}, creatore {creatore}")
            else:
                logger.info(f"[Lotto #{id_lotto}] Nessun lotto trovato nella catena di tracciabilità")
                
            return (ids, creatori)
        except Exception as e:
            logger.error(f"[Lotto #{id_lotto}] Errore nel recupero della catena di tracciabilità: {e}")
            raise Exception(f"Errore durante il recupero della catena di tracciabilità: {str(e)}")

        
    def get_all_comp(self):
        """
        Recupera tutte le composizioni di lotti registrate sulla blockchain.
        """
        try:
            logger.info("Recupero di tutte le composizioni di lotti dalla blockchain")
            composizioni = self.contract.functions.getAllComposizioni().call()
            
            if composizioni and len(composizioni) > 0:
                logger.info(f"Trovate {len(composizioni)} composizioni di lotti sulla blockchain")
            else:
                logger.info("Nessuna composizione di lotti trovata sulla blockchain")
                
            return composizioni
        except Exception as e:
            logger.error(f"Errore nel recupero delle composizioni di lotti: {e}")
            raise Exception(f"Errore durante il recupero delle composizioni di lotti: {str(e)}")
        
    def get_my_token_balance(self):
        try:
            # Ottieni l'indirizzo dell'account corrente
            address = self.get_address()
            checksum_address = Web3.to_checksum_address(address)
            
            # Chiama la funzione del contratto
            balance = self.contract.functions.getMyTokenBalance().call({
                'from': checksum_address
            })
            
            logger.info(f"Balance recuperato per l'indirizzo {address}: {balance}")
            return balance
            
        except Exception as e:
            logger.error(f"Errore nel recupero del balance: {e}")
            raise Exception(f"Errore durante il recupero del balance: {str(e)}")
        

            
    def is_company_registered(self, address):
        """Verifica se un indirizzo Ethereum è registrato come azienda sulla blockchain
        
        Args:
            address: L'indirizzo Ethereum da verificare
            
        Returns:
            bool: True se l'azienda è registrata, False altrimenti
        """
        try:
            checksum_address = Web3.to_checksum_address(address)
            is_registered = self.contract.functions.isCompanyAddressRegistered(checksum_address).call()
            logger.info(f"Verifica registrazione per l'indirizzo {address}: {is_registered}")
            return is_registered
        except Exception as e:
            logger.error(f"Errore nella verifica della registrazione dell'azienda {address}: {e}")
            return False
            
    def firma_richiesta_token(self, destinatario, quantita):
        """
        Gestisce la firma di una richiesta di token tramite MetaMask.
        
        Args:
            destinatario: L'ID dell'azienda destinataria della richiesta
            quantita: La quantità di token richiesti
        
        Returns:
            str: L'esito dell'operazione
        """
        account = self.get_address()  # Funzione che recupera account locale

        # Crea un messaggio descrittivo per la richiesta di token
        messaggio = f"Conferma richiesta di {quantita} token all'azienda con ID {destinatario}"
        messaggio_encoded = messaggio.replace(" ", "%20")

        # Costruisci l'URL con tutti i parametri necessari
        url = f"http://localhost:5001/firma_richiesta_token.html?messaggio={messaggio_encoded}&destinatario={destinatario}&quantita={quantita}"
        
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                proc = subprocess.Popen([chrome_path, url])
                proc.wait()
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            raise Exception(f"Errore nell'apertura del browser: {str(e)}")
        
        # Attendi la risposta dal servizio web
        max_wait = 60  # secondi
        wait_interval = 3  # secondi
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                print(f"Attendo esito richiesta token per l'account {account} e destinatario {destinatario}")
                response = requests.get(f"http://localhost:5001/esito_richiesta_token/{account}/{destinatario}", timeout=10)
                data = response.json()
                if "esito" in data:
                    esito = data["esito"]
                    logger.info(f"Esito richiesta token: {esito}")
                    return esito
            except requests.RequestException as e:
                print(f"Errore nella richiesta HTTP: {e}")
                pass  # Continua a riprovare

            time.sleep(wait_interval)

        raise TimeoutError("Timeout in attesa della firma tramite MetaMask")

    def firma_accettazione_token(self, id_richiesta, mittente, quantita):
        """
        Gestisce la firma di un'accettazione di token tramite MetaMask.
        
        Args:
            id_richiesta: L'ID della richiesta di token
            mittente: L'ID dell'azienda mittente della richiesta
            quantita: La quantità di token richiesti
        
        Returns:
            str: L'esito dell'operazione
        """
        account = self.get_address()  # Funzione che recupera account locale

        # Crea un messaggio descrittivo per l'accettazione di token
        messaggio = f"Conferma accettazione richiesta di {quantita} token da parte dell'azienda con ID {mittente} (richiesta #{id_richiesta})"
        messaggio_encoded = messaggio.replace(" ", "%20")

        # Costruisci l'URL con tutti i parametri necessari
        url = f"http://localhost:5001/firma_accetta_token.html?messaggio={messaggio_encoded}&mittente={mittente}&quantita={quantita}&id_richiesta={id_richiesta}"
        
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                proc = subprocess.Popen([chrome_path, url])
                proc.wait()
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            raise Exception(f"Errore nell'apertura del browser: {str(e)}")
        
        # Attendi la risposta dal servizio web
        max_wait = 60  # secondi
        wait_interval = 3  # secondi
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                print(f"Attendo esito accettazione token per l'account {account} e richiesta {id_richiesta}")
                response = requests.get(f"http://localhost:5001/esito_accettazione_token/{account}/{id_richiesta}", timeout=10)
                data = response.json()
                if "esito" in data:
                    esito = data["esito"]
                    logger.info(f"Esito accettazione token: {esito}")
                    return esito
            except requests.RequestException as e:
                print(f"Errore nella richiesta HTTP: {e}")
                pass  # Continua a riprovare

            time.sleep(wait_interval)

        raise TimeoutError("Timeout in attesa della firma tramite MetaMask")

    def crea_richiesta_token(self, provider_address, amount, purpose, co2_reduction, account_address):
        """
        Crea una richiesta di token sulla blockchain.
        
        Args:
            provider_address: Indirizzo dell'azienda che fornisce i token
            amount: Quantità di token richiesti
            purpose: Scopo della richiesta (sostenibilità)
            co2_reduction: Stima della riduzione di CO2
            account_address: Indirizzo dell'account che effettua la richiesta
            
        Returns:
            str: Hash della transazione
        """
        try:
            # Converti l'indirizzo del provider in formato checksum
            provider_address_checksum = Web3.to_checksum_address(provider_address)
            requester_address_checksum = Web3.to_checksum_address(account_address)
            
            logger.info(f"Invio richiesta token: provider={provider_address_checksum}, amount={amount}, purpose={purpose}, co2_reduction={co2_reduction}")
            
            # Ottieni il nonce per l'account
            nonce = w3.eth.get_transaction_count(requester_address_checksum)
            
            # Costruisci la transazione
            txn = self.contract.functions.createTokenRequest(
                provider_address_checksum,
                amount,
                purpose,
                co2_reduction
            ).build_transaction({
                'from': requester_address_checksum,
                'gas': 2000000,  # Gas limit
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # NOTA: In un ambiente reale, qui dovremmo firmare la transazione con la chiave privata
            # Ma poiché stiamo usando Hardhat in modalità sviluppo, possiamo inviare direttamente
            # la transazione senza firmarla, e Hardhat la firmerà automaticamente
            
            # Invia la transazione
            tx_hash = w3.eth.send_transaction(txn)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Verifica lo stato della transazione
            if tx_receipt['status'] == 1:
                logger.info(f"Richiesta token inviata con successo. Tx hash: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                error_msg = f"Errore nell'invio della richiesta token. Transazione fallita. Status: {tx_receipt['status']}"
                logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Errore nell'invio della richiesta token sulla blockchain: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        

    def accetta_richiesta_token(self, id_richiesta,account_address):
        """
        Crea una richiesta di token sulla blockchain.
        
        Args:
            provider_address: Indirizzo dell'azienda che fornisce i token
            amount: Quantità di token richiesti
            purpose: Scopo della richiesta (sostenibilità)
            co2_reduction: Stima della riduzione di CO2
            account_address: Indirizzo dell'account che effettua la richiesta
            
        Returns:
            str: Hash della transazione
        """
        try:
            
            requester_address_checksum = Web3.to_checksum_address(account_address)
            
            logger.info(f"Accetto richiesta token: provider={account_address}, id={id_richiesta}")
            
            # Ottieni il nonce per l'account
            nonce = w3.eth.get_transaction_count(requester_address_checksum)
            
            # Costruisci la transazione
            txn = self.contract.functions.acceptTokenRequest(
                id_richiesta
            ).build_transaction({
                'from': requester_address_checksum,
                'gas': 2000000,  # Gas limit
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # NOTA: In un ambiente reale, qui dovremmo firmare la transazione con la chiave privata
            # Ma poiché stiamo usando Hardhat in modalità sviluppo, possiamo inviare direttamente
            # la transazione senza firmarla, e Hardhat la firmerà automaticamente
            
            # Invia la transazione
            tx_hash = w3.eth.send_transaction(txn)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Verifica lo stato della transazione
            if tx_receipt['status'] == 1:
                logger.info(f"Accettazione token inviata con successo. Tx hash: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                error_msg = f"Errore nell'accettazione della richiesta token. Transazione fallita. Status: {tx_receipt['status']}"
                logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Errore nell'accettazione della richiesta token sulla blockchain: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)