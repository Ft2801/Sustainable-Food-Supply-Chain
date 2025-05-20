# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import sqlite3
import json
import os
import subprocess
import requests
import sys
import re
from configuration.database import Database
from model.richiesta_model import RichiestaModel
from model.richiesta_token_model import RichiestaTokenModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl import db_default_string
from configuration.log_load_setting import logger

# Funzione di supporto per generare script JavaScript con i percorsi corretti
def generate_js_script(script_type, params):
    """Genera uno script JavaScript per interagire con la blockchain.
    
    Args:
        script_type: Tipo di script (accept_token, reject_token, create_token)
        params: Parametri per lo script
        
    Returns:
        Script JavaScript come stringa
    """
    # Utilizza il percorso artifacts/contracts come in interact_contract.py
    contract_path = "../artifacts/contracts/TokenExchange.sol/TokenExchange.json"
    
    # Script base compatibile con ethers.js v5 e v6
    base_script = f'''
    // Importa ethers e verifica la versione
    const ethers = require("ethers");
    const fs = require("fs");
    const path = require("path");

    async function main() {{
        try {{
            // Verifica la versione di ethers.js
            const isEthersV6 = ethers.version && parseInt(ethers.version.split('.')[0]) >= 6;
            console.log(`Usando ethers.js ${{isEthersV6 ? 'v6+' : 'v5-'}}`);
            
            // Configura il provider in modo compatibile con entrambe le versioni
            let provider;
            if (isEthersV6) {{
                provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
            }} else {{
                provider = new ethers.providers.JsonRpcProvider("http://127.0.0.1:8545");
            }}
            
            // Carica l'ABI del contratto
            const contractPath = path.join(__dirname, "{contract_path}");
            const contractJson = JSON.parse(fs.readFileSync(contractPath));
            
            // Ottieni il signer in modo compatibile con entrambe le versioni
            let signer;
            if (isEthersV6) {{
                const accounts = await provider.listAccounts();
                signer = await provider.getSigner(accounts[0].address);
            }} else {{
                const accounts = await provider.listAccounts();
                signer = provider.getSigner(accounts[0]);
            }}
    '''
    
    if script_type == "accept_token":
        return base_script + f'''
            // Crea un'istanza del contratto
            const contract = new ethers.Contract(
                "{params['contract_address']}",
                contractJson.abi,
                signer
            );
            
            // Esegui la transazione
            const tx = await contract.acceptTokenRequest({params['request_id']});
            console.log("Transaction hash:", tx.hash);
            
            // Attendi la conferma della transazione
            const receipt = await tx.wait();
            console.log("Transaction confirmed in block:", receipt.blockNumber);
            console.log("Transaction status:", receipt.status);
            
            process.exit(0);
        }} catch (error) {{
            console.error("Error:", error.message);
            process.exit(1);
        }}
    }}
    
    main();
    '''
    elif script_type == "reject_token":
        return base_script + f'''
            // Crea un'istanza del contratto
            const contract = new ethers.Contract(
                "{params['contract_address']}",
                contractJson.abi,
                signer
            );
            
            // Esegui la transazione
            const tx = await contract.rejectTokenRequest({params['request_id']}, "{params['reason']}");
            console.log("Transaction hash:", tx.hash);
            
            // Attendi la conferma della transazione
            const receipt = await tx.wait();
            console.log("Transaction confirmed in block:", receipt.blockNumber);
            console.log("Transaction status:", receipt.status);
            
            process.exit(0);
        }} catch (error) {{
            console.error("Error:", error.message);
            process.exit(1);
        }}
    }}
    
    main();
    '''
    elif script_type == "create_token":
        return base_script + f'''
            // Crea un'istanza del contratto
            const contract = new ethers.Contract(
                "{params['contract_address']}",
                contractJson.abi,
                signer
            );
            
            // Esegui la transazione
            const tx = await contract.createTokenRequest(
                "{params['provider_address']}",
                "{params['token_contract_address']}",
                {params['amount']},
                "{params['purpose']}",
                {params['co2_reduction']}
            );
            console.log("Transaction hash:", tx.hash);
            
            // Attendi la conferma della transazione
            const receipt = await tx.wait();
            console.log("Transaction confirmed in block:", receipt.blockNumber);
            console.log("Transaction status:", receipt.status);
            
            // Ottieni l'ID della richiesta creata
            const requestId = await contract.getLastRequestId();
            console.log("Request ID:", requestId.toString());
            
            process.exit(0);
        }} catch (error) {{
            console.error("Error:", error.message);
            process.exit(1);
        }}
    }}
    
    main();
    '''
    else:
        raise ValueError(f"Tipo di script non supportato: {script_type}")


# Configurazione ethers.js e Hardhat per la blockchain
class BlockchainConfig:
    def __init__(self):
        # Inizializzazione delle variabili per la connessione blockchain
        self.contract_abis = {}
        self.contract_addresses = {}
        self.contracts = {}
        self.hardhat_url = "http://127.0.0.1:8545"  # URL predefinito per Hardhat
        
        # Flag per indicare se la blockchain è disponibile
        self.blockchain_available = False
        
        # Tenta di inizializzare la connessione blockchain
        try:
            # Verifica se la rete Hardhat è attiva
            response = requests.get(self.hardhat_url, timeout=5)
            if response.status_code == 200:
                self.blockchain_available = True
                self.load_contract_info()
                self.initialize_contracts()
                logger.info("Connessione alla blockchain Hardhat stabilita con successo")
            else:
                logger.warning("Impossibile connettersi alla blockchain Hardhat. Funzionalità blockchain disabilitate.")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Errore di connessione alla blockchain Hardhat: {e}. Funzionalità blockchain disabilitate.")
        except Exception as e:
            logger.warning(f"Errore nell'inizializzazione della blockchain: {e}. Funzionalità blockchain disabilitate.")
    
    def load_contract_info(self):
        """Carica gli ABI e gli indirizzi dei contratti dai file JSON compilati"""
        if not self.blockchain_available:
            return
            
        try:
            contract_names = ["CO2Token", "TokenExchange", "CompanyRegistry", "UserRegistry"]
            # Percorso per i contratti compilati (usando la directory artifacts/contracts come in interact_contract.py)
            artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                       "on_chain", "artifacts", "contracts")
            
            logger.info(f"Cercando contratti in: {artifacts_dir}")
            
            # Ottieni gli indirizzi dei contratti deployati
            # Usiamo il modulo interact_contract per ottenere gli indirizzi corretti
            try:
                sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "on_chain"))
                from interact_contract import BlockchainInteractor
                interactor = BlockchainInteractor()
                
                # Ottieni i contratti dal BlockchainInteractor
                for contract_name, contract in interactor.contracts.items():
                    if contract_name in contract_names:
                        self.contract_addresses[contract_name] = contract.address
                        self.contract_abis[contract_name] = contract.abi
                        logger.info(f"Contratto {contract_name} caricato da BlockchainInteractor con indirizzo: {contract.address}")
            except Exception as e:
                logger.warning(f"Errore nell'utilizzo di BlockchainInteractor: {e}")
                logger.warning("Utilizzando il metodo alternativo per caricare i contratti")
                
                # Metodo alternativo: cerca i file JSON nelle sottodirectory di artifacts_dir
                for contract_name in contract_names:
                    try:
                        # Cerca il file JSON corrispondente al contratto
                        contract_files = []
                        for root, dirs, files in os.walk(artifacts_dir):
                            for file in files:
                                if file.endswith('.json') and not file.endswith('.dbg.json'):
                                    file_path = os.path.join(root, file)
                                    try:
                                        with open(file_path, 'r') as f:
                                            contract_data = json.load(f)
                                            if 'contractName' in contract_data and contract_data['contractName'] == contract_name:
                                                contract_files.append((file_path, contract_data))
                                    except Exception as file_error:
                                        logger.warning(f"Errore nella lettura del file {file_path}: {file_error}")
                        
                        if contract_files:
                            # Usa il primo file trovato
                            file_path, contract_data = contract_files[0]
                            self.contract_abis[contract_name] = contract_data['abi']
                            logger.info(f"ABI per il contratto {contract_name} trovato in {file_path}")
                            
                            # Per gli indirizzi, dobbiamo usare quelli trovati da BlockchainInteractor
                            # o quelli predefiniti di Hardhat
                            if contract_name == "TokenExchange":
                                self.contract_addresses[contract_name] = "0xa513E6E4b8f2a923D98304ec87F64353C4D5C853"
                                logger.info(f"Contratto TokenExchange mappato all'indirizzo: {self.contract_addresses[contract_name]}")
                            elif contract_name == "UserRegistry":
                                self.contract_addresses[contract_name] = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
                                logger.info(f"Contratto UserRegistry mappato all'indirizzo: {self.contract_addresses[contract_name]}")
                            elif contract_name == "CO2Token":
                                # Dai log, il primo contratto trovato è probabilmente CO2Token
                                self.contract_addresses[contract_name] = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
                                logger.info(f"Contratto CO2Token mappato all'indirizzo: {self.contract_addresses[contract_name]}")
                            elif contract_name == "CompanyRegistry":
                                self.contract_addresses[contract_name] = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
                                logger.info(f"Contratto CompanyRegistry mappato all'indirizzo: {self.contract_addresses[contract_name]}")
                            else:
                                # Indirizzo fittizio per test
                                self.contract_addresses[contract_name] = f"0x{contract_name}000000000000000000000000000000000000"
                            
                            logger.info(f"Contratto {contract_name} configurato con indirizzo: {self.contract_addresses[contract_name]}")
                        else:
                            logger.warning(f"Nessun file trovato per il contratto {contract_name}")
                    except Exception as e:
                        logger.warning(f"Errore nel caricamento del contratto {contract_name}: {e}")
        except Exception as e:
            logger.warning(f"Errore nel caricamento dei contratti: {e}")
            self.blockchain_available = False
    
    def initialize_contracts(self):
        """Inizializza i contratti con gli ABI e gli indirizzi caricati"""
        if not self.blockchain_available:
            return
            
        try:
            # In questo metodo, memorizziamo solo le informazioni sui contratti
            # L'interazione effettiva avverrà tramite chiamate API a Hardhat
            for contract_name, abi in self.contract_abis.items():
                if contract_name in self.contract_addresses:
                    self.contracts[contract_name] = {
                        'address': self.contract_addresses[contract_name],
                        'abi': abi
                    }
                    logger.info(f"Contratto {contract_name} inizializzato con successo")
                else:
                    logger.warning(f"Impossibile inizializzare il contratto {contract_name}: indirizzo mancante")
        except Exception as e:
            logger.warning(f"Errore nell'inizializzazione dei contratti: {e}")
            self.blockchain_available = False
    
    def get_account_from_id(self, id_azienda):
        """Ottiene l'indirizzo Ethereum associato all'ID azienda"""
        if not self.blockchain_available:
            return None
            
        try:
            # Cerca l'indirizzo associato all'azienda nel database o nel registro aziendale
            # Per ora usiamo una simulazione, ma in futuro dovremmo implementare una query
            # al contratto CompanyRegistry o a un database locale che mappa gli ID alle aziende
            
            # Simulazione: restituisce un indirizzo fittizio basato sull'ID azienda
            return f"0x{id_azienda:040x}"  # Indirizzo fittizio basato sull'ID
        except Exception as e:
            logger.warning(f"Errore nel recupero dell'indirizzo Ethereum: {e}")
            return None

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
        """
        Recupera le operazioni di token per un'azienda dal database locale.
        Se la blockchain è disponibile, tenta di recuperare anche da lì.
        """
        try:
            # Recupera le operazioni dal database locale
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
            logger.info(f"Operazioni token recuperate dal database: {len(risultati_raw) if risultati_raw else 0}")
            
            # Tenta di inizializzare la connessione blockchain (ma non blocca se fallisce)
            try:
                blockchain_config = BlockchainConfig()
                if blockchain_config.blockchain_available:
                    logger.info("Blockchain disponibile, tentativo di recupero operazioni token dalla blockchain")
                    # Implementazione futura: recupero operazioni dalla blockchain
                    # Questo codice è commentato per evitare errori, ma mostra come potrebbe essere implementato
                    # in futuro quando la blockchain sarà pienamente integrata
                    """
                    eth_address = blockchain_config.get_account_from_id(id_azienda)
                    if eth_address and 'TokenExchange' in blockchain_config.contracts:
                        token_exchange = blockchain_config.contracts['TokenExchange']
                        sustainable_requests = token_exchange.functions.getSustainableRequests(0, False).call()
                        # Elaborazione dei risultati...
                    """
            except Exception as e:
                logger.warning(f"Errore nel tentativo di recupero dalla blockchain: {e}")
                # Continua con i risultati del database locale
            
            return [RichiestaTokenModel(*r) for r in risultati_raw] if risultati_raw else []
        except Exception as e:
            logger.error(f"Errore nel recupero delle operazioni di token: {e}", exc_info=True)
            return []
    
    def register_company_on_blockchain(self, id_azienda):
        """Registra un'azienda sulla blockchain se non è già registrata
        
        Args:
            id_azienda: ID dell'azienda da registrare
            
        Returns:
            True se l'operazione è riuscita, False altrimenti
        """
        try:
            # Per ora, assumiamo che l'azienda sia già registrata o che non sia necessario registrarla
            # Questo è un workaround temporaneo per consentire il funzionamento dell'applicazione
            # In una versione futura, implementeremo la registrazione effettiva dell'azienda
            logger.info(f"Simulazione registrazione azienda {id_azienda} sulla blockchain")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella registrazione dell'azienda sulla blockchain: {e}")
            return False

    def update_richiesta_token(self, richiesta: RichiestaTokenModel, stato : str) -> None:
        """
        Aggiorna lo stato di una richiesta di token nel database locale.
        Se la blockchain è disponibile, tenta di sincronizzare anche lì.
        """
        try:
            # Aggiornamento nel database locale
            queries = []
            
            # Aggiornamento dello stato
            query_mag = """UPDATE RichiestaToken SET stato = ? WHERE id_richiesta = ?;""" 
            value_mag = (stato, richiesta.id_richiesta)
            queries.append((query_mag, value_mag))
            
            # Trasferimento token solo se la richiesta è accettata
            if stato == db_default_string.STATO_ACCETTATA:
                # Verifica che l'azienda destinataria (fornitore) abbia token sufficienti
                check_query = "SELECT Token FROM Azienda WHERE Id_azienda = ?"
                token_disponibili = self.db.fetch_one(check_query, (richiesta.id_destinatario,))
                
                if token_disponibili is None:
                    raise ValueError(f"Impossibile verificare i token disponibili per l'azienda {richiesta.destinatario}")
                    
                if token_disponibili < richiesta.quantita:
                    raise ValueError(f"L'azienda {richiesta.destinatario} non ha token sufficienti. Disponibili: {token_disponibili}, Richiesti: {richiesta.quantita}")
                
                # Sottrai token dall'azienda destinataria (fornitore di token)
                query_mag = """UPDATE Azienda SET Token = Token - ? WHERE Id_azienda = ? AND Token >= ?;""" 
                value_mag = (richiesta.quantita, richiesta.id_destinatario, richiesta.quantita)
                queries.append((query_mag, value_mag))
                
                # Aggiungi token all'azienda mittente (richiedente di token)
                query_mag = """UPDATE Azienda SET Token = Token + ? WHERE Id_azienda = ?;""" 
                value_mag = (richiesta.quantita, richiesta.id_mittente)
                queries.append((query_mag, value_mag))
            
            # Esegui la transazione nel database locale
            self.db.execute_transaction(queries)
            logger.info(f"Richiesta con ID {richiesta.id_richiesta} aggiornata a {stato} nel database locale.")
            
            # Sincronizzazione con la blockchain (OBBLIGATORIA per lo scambio di token)
            blockchain_config = BlockchainConfig()
            if not blockchain_config.blockchain_available and stato == db_default_string.STATO_ACCETTATA:
                # Se la blockchain non è disponibile e stiamo cercando di accettare una richiesta,
                # dobbiamo bloccare l'operazione
                logger.error("Impossibile completare l'operazione: la blockchain non è disponibile")
                raise ValueError("La blockchain è obbligatoria per lo scambio di token. Impossibile completare l'operazione.")
            
            if blockchain_config.blockchain_available:
                logger.info("Blockchain disponibile, sincronizzazione dell'aggiornamento")
                try:
                    provider_address = blockchain_config.get_account_from_id(richiesta.id_destinatario)
                    requester_address = blockchain_config.get_account_from_id(richiesta.id_mittente)
                    
                    if provider_address and requester_address and 'TokenExchange' in blockchain_config.contracts:
                        token_exchange = blockchain_config.contracts['TokenExchange']
                        
                        # Crea uno script temporaneo per interagire con la blockchain tramite ethers.js
                        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                                "on_chain", "scripts")
                        os.makedirs(scripts_dir, exist_ok=True)
                        
                        if stato == db_default_string.STATO_ACCETTATA:
                            # Script per accettare la richiesta di token
                            script_path = os.path.join(scripts_dir, "accept_token_request.js")
                            
                            # Prepara i parametri per lo script
                            script_params = {
                                'contract_address': token_exchange['address'],
                                'request_id': richiesta.id_richiesta
                            }
                            
                            # Genera lo script
                            script_content = generate_js_script("accept_token", script_params)
                            
                            # Scrivi lo script su file
                            with open(script_path, 'w') as f:
                                f.write(script_content)
                            
                            # Esegui lo script Node.js
                            logger.info(f"Esecuzione dello script per accettare la richiesta di token: {script_path}")
                            result = subprocess.run(["node", script_path], capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                logger.info(f"Transazione di accettazione completata: {result.stdout}")
                            else:
                                logger.error(f"Errore nell'esecuzione dello script: {result.stderr}")
                                raise ValueError(f"Errore nella transazione blockchain: {result.stderr}")
                                
                        elif stato == db_default_string.STATO_RIFIUTATA:
                            # Script per rifiutare la richiesta di token
                            script_path = os.path.join(scripts_dir, "reject_token_request.js")
                            
                            # Prepara i parametri per lo script
                            script_params = {
                                'contract_address': token_exchange['address'],
                                'request_id': richiesta.id_richiesta,
                                'reason': "Richiesta rifiutata dall'utente"
                            }
                            
                            # Genera lo script
                            script_content = generate_js_script("reject_token", script_params)
                            
                            # Scrivi lo script su file
                            with open(script_path, 'w') as f:
                                f.write(script_content)
                            
                            # Esegui lo script Node.js
                            logger.info(f"Esecuzione dello script per rifiutare la richiesta di token: {script_path}")
                            result = subprocess.run(["node", script_path], capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                logger.info(f"Transazione di rifiuto completata: {result.stdout}")
                            else:
                                logger.warning(f"Errore nell'esecuzione dello script: {result.stderr}")
                                # Per il rifiuto, possiamo continuare con l'aggiornamento locale
                except Exception as e:
                    logger.error(f"Errore nella sincronizzazione con la blockchain: {e}")
                    # Se c'è un errore nella blockchain durante l'accettazione, dobbiamo bloccare l'operazione
                    if stato == db_default_string.STATO_ACCETTATA:
                        raise ValueError(f"Errore nella sincronizzazione con la blockchain: {e}")
                    # Per il rifiuto, possiamo continuare con l'aggiornamento locale
        
        except sqlite3.IntegrityError as e:
            logger.error(f"Errore di integrità nel database: {e}", exc_info=True)
            raise ValueError("Non disponi di token sufficienti")
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento della richiesta: {e}", exc_info=True)
            raise e
        
    def send_richiesta_token(self, mittente: int, destinatario: int, quantita: int) -> str:
        """Invia una richiesta di token da un'azienda a un'altra
        
        Args:
            mittente: ID dell'azienda mittente
            destinatario: ID dell'azienda destinataria
            quantita: Quantità di token richiesti
            
        Returns:
            ID della richiesta creata
        """
        try:
            # Verifica che le aziende esistano
            query_mittente = "SELECT Nome, Tipo FROM Azienda WHERE Id_azienda = ?"
            mittente_info = self.db.fetch_one(query_mittente, (mittente,))
            
            query_dest = "SELECT Nome, Tipo FROM Azienda WHERE Id_azienda = ?"
            dest_info = self.db.fetch_one(query_dest, (destinatario,))
            
            if not mittente_info or not dest_info:
                raise ValueError("Azienda mittente o destinataria non trovata")
            
            # Verifica che le aziende non siano di tipo 'Certificatore'
            if mittente_info[1] == 'Certificatore':
                raise ValueError("Le aziende di tipo 'Certificatore' non possono inviare richieste di token")
            
            if dest_info[1] == 'Certificatore':
                raise ValueError("Le aziende di tipo 'Certificatore' non possono ricevere richieste di token")
            
            # Verifica che la quantità sia valida
            if quantita <= 0:
                raise ValueError("La quantità deve essere maggiore di zero")
            
            # Inserisci la richiesta nel database locale
            # Lasciamo che SQLite generi automaticamente l'ID
            query = """INSERT INTO RichiestaToken (Id_richiedente, Id_ricevente, Quantita, Stato)
                       VALUES (?, ?, ?, ?)"""
            self.db.execute_query(query, (mittente, destinatario, quantita, "In attesa"))
            
            # Ottieni l'ID della richiesta appena inserita
            id_query = "SELECT last_insert_rowid()"
            result = self.db.fetch_one(id_query)
            
            # Gestisci il caso in cui il risultato sia già un intero o una tupla
            if isinstance(result, tuple):
                id_richiesta = result[0]
            else:
                id_richiesta = result
                
            logger.info(f"ID della richiesta inserita: {id_richiesta}")
            
            logger.info(f"Richiesta di token inserita nel database locale da {mittente_info[0]} a {dest_info[0]}")
            
            # Simula la registrazione sulla blockchain
            logger.info(f"Simulazione della registrazione della richiesta {id_richiesta} sulla blockchain")
            
            # In una versione futura, qui verrà implementata la vera registrazione sulla blockchain
            # Per ora, utilizziamo un ID fittizio per la richiesta sulla blockchain
            blockchain_request_id = "123456"
            
            # Prima di aggiornare, verifichiamo se la colonna blockchain_request_id esiste
            try:
                # Verifica se la colonna esiste
                check_query = "PRAGMA table_info(RichiestaToken)"
                columns = self.db.fetch_all(check_query)
                column_names = [col[1] for col in columns]
                
                if 'blockchain_request_id' in column_names:
                    # Aggiorna il record locale con l'ID della richiesta sulla blockchain
                    update_query = "UPDATE RichiestaToken SET blockchain_request_id = ? WHERE Id_richiesta = ?"
                    self.db.execute_query(update_query, (blockchain_request_id, id_richiesta))
                    logger.info(f"Aggiornato blockchain_request_id per la richiesta {id_richiesta}")
                else:
                    logger.info(f"La colonna blockchain_request_id non esiste nella tabella RichiestaToken, l'aggiornamento viene saltato")
            except Exception as e:
                # Se c'è un errore, lo logghiamo ma continuiamo
                logger.warning(f"Impossibile aggiornare blockchain_request_id: {e}")
                # Non solleviamo un'eccezione qui, poiché non è un errore critico
            
            logger.info(f"Richiesta di token {id_richiesta} registrata con successo")
            return id_richiesta
            
        except Exception as e:
            logger.error(f"Errore nell'invio della richiesta di token: {e}", exc_info=True)
            raise ValueError(f"Errore nell'invio della richiesta di token: {e}")