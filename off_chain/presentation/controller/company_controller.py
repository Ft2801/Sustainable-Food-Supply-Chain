# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
# pylint: disable= C0103 # Ignora gli errori di nome variabile/metodo come richiesto
# pylint: disable= R0913 # Ignora 'Too many arguments'
# pylint: disable= R0917 # Ignora 'Too many positional arguments'

import datetime
from configuration.log_load_setting import logger # Importato una sola volta
from model.threshold_model import ThresholdModel
from model.prodotto_finito_model import ProdottoLottoModel
from model.info_product_for_choice_model import ProductForChoiceModel
from model.product_standard_model import ProductStandardModel
from model.company_model import CompanyModel
from model.operation_estesa_model import OperazioneEstesaModel
from model.compensation_action_model import CompensationActionModel
from model.prodotto_finito_model import ProdottoLottoModel
from model.richiesta_model import RichiestaModel
from model.richiesta_token_model import RichiestaTokenModel
from session import Session
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.compensation_action_repository_impl import CompensationActionRepositoryImpl
from persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl


PERMESSI_OPERAZIONI = {
    "Agricola": ["Produzione"],
    "Trasportatore": ["Trasporto"],
    "Trasformatore": ["Trasformazione"],
    "Rivenditore": ["Rivendita"]
}


class ControllerAzienda:
    """
    As the instance has been created, in the repository implement layer, to access your methods,
    we initialize the instances of the classes 'class instances' with:
            OperationRepositoryImpl()
            ProductRepositoryImpl()
            ThresholdRepositoryImpl()
            CompanyRepositoryImpl()
    """

    def __init__(self):
        self.operation_repository = OperationRepositoryImpl()
        self.compensation_action = CompensationActionRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        self.richieste = RichiesteRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")

    def lista_soglie(self) -> list[ThresholdModel]:
        lista_soglie = self.threshold.get_lista_soglie()
        return lista_soglie

    def get_prodotti_to_composizione(self) -> list[ProdottoLottoModel]:
        try:
            return self.product.get_prodotti_finiti_magazzino_azienda(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)
            return []

    def lista_operazioni(self, azienda: int) -> list[OperazioneEstesaModel]:
        try:
            lista_operazioni = self.operation_repository.get_operazioni_by_azienda(azienda)
            return lista_operazioni
        except Exception as e:
            logger.error(f"Error al obtener la lista di operazioni: {e}", exc_info=True)
            return []

    def lista_azioni_compensative(self, azienda: int) -> list[CompensationActionModel]:
        try:
            lista_azioni_compensative = self.compensation_action.get_lista_azioni(azienda)
            return lista_azioni_compensative
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle azioni compensative: {e}", exc_info=True)
            return []

    def get_materie_prime_magazzino_azienda(self) -> list[ProdottoLottoModel]:
        try:
            materie_prime = self.product.get_materie_prime_magazzino_azienda(Session().current_user["id_azienda"])
            return materie_prime
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle materie prime: {e}", exc_info=True)
            return []

    def get_prodotti_finiti_magazzino_azienda(self) -> list[ProdottoLottoModel]:
        try:
            prodotti_finiti = self.product.get_prodotti_finiti_magazzino_azienda(Session().current_user["id_azienda"])
            return prodotti_finiti
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle materie prime: {e}", exc_info=True)
            return []

    def crea_prodotto_trasformato(self, id_tipo: int, descrizione: str, quantita: int,
                                  quantita_usata_per_materia: dict[ProdottoLottoModel, int], co2: int):
        try:
            id_azienda = Session().current_user["id_azienda"]
            self.operation_repository.inserisci_prodotto_trasformato(
                id_tipo, descrizione, quantita, quantita_usata_per_materia,
                id_azienda, co2_consumata=co2
            )
        except Exception as e:
            logger.error(f"Errore nella creazione del prodotto trasformato: {e}", exc_info=True)

    def salva_operazione_agricola(self, tipo: str, data: datetime,
                                  co2: float, id_tipo_prodotto: int, descrizione: str, quantita: int
                                 ):
        if not self.check_utente(tipo):
            raise PermissionError("Operazione non consentita per questo utente.")

        self.operation_repository.inserisci_operazione_azienda_agricola(
            id_tipo_prodotto, descrizione, quantita, Session().current_user["id_azienda"], data, co2,
        )

    def salva_operazione_distributore(self, data: datetime, co2: float, id_prodotto,
                                      id_lotto_input: int, quantita: int):
        try:
            self.operation_repository.inserisci_operazione_azienda_rivenditore(
                Session().current_user["id_azienda"],
                id_prodotto, data, co2, "vendita", id_lotto_input, quantita
            )
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)

    def salva_operazione_trasporto(self, id_prodotto: int, id_azienda_ricevente: int,
                                   id_azienda_richiedente: int, quantita: int, co2: float,
                                   id_lotto_input: int):
        self.operation_repository.inserisci_operazione_trasporto(
            Session().current_user["id_azienda"], id_lotto_input, id_prodotto,
            id_azienda_richiedente, id_azienda_ricevente, quantita, co2
        )

    def get_prodotti_ordinabili(self) -> list[ProductForChoiceModel]:
        try:
            if Session().current_user["role"] == "Rivenditore":
                prodotti = self.product.get_prodotti_ordinabili(1)
            else:
                prodotti = self.product.get_prodotti_ordinabili()
            return prodotti
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista dei prodotti ordinabili: {e}", exc_info=True)
            return []

    def get_aziende_trasporto(self) -> list[CompanyModel]:
        try:
            aziende = self.company.get_aziende_trasporto()
            return aziende
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle aziende di trasporto: {e}", exc_info=True)
            return []

    def invia_richiesta(self, id_az_ricevente: int, id_az_trasporto: int,
                        id_prodotto: int, quantita: int):
        try:
            self.richieste.inserisci_richiesta(
                Session().current_user["id_azienda"], id_az_ricevente,
                id_az_trasporto, id_prodotto, quantita
            )
        except Exception as e:
            logger.error(f"Errore nell'invio della richiesta: {e}", exc_info=True)

    def get_richieste_ricevute(self) -> list[RichiestaModel]:
        try:
            if Session().current_user["role"] == "Trasportatore":
                richieste = self.richieste.get_richieste_ricevute(
                    Session().current_user["id_azienda"], check_trasporto=True
                )
            else:
                richieste = self.richieste.get_richieste_ricevute(
                    Session().current_user["id_azienda"]
                )
            return richieste
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle richieste ricevute: {e}", exc_info=True)
            return []

    def get_richieste_effettuate(self) -> list[RichiestaModel]:
        try:
            richieste = self.richieste.get_richieste_effettuate(Session().current_user["id_azienda"])
            return richieste
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle richieste effettuate: {e}", exc_info=True)
            return []

    def update_richiesta(self, id_richiesta: int, nuovo_stato: str):
        try:
            self.richieste.update_richiesta(id_richiesta, nuovo_stato, Session().current_user["role"])
        except Exception as e: # W0719: Cattura eccezione generica
            logger.error(f"Errore nell'aggiornare la richiesta: {e}", exc_info=True)
            raise Exception(f"Errore nell'aggiornare la richiesta: {str(e)}") from e

    def check_utente(self, tipo_operazione: str) -> bool:
        return tipo_operazione in PERMESSI_OPERAZIONI.get(Session().current_user["role"], [])

    def aggiungi_azione_compensativa(self, descrizione, co2, data):
        try:
            self.compensation_action.inserisci_azione(
                data=data, azienda=Session().current_user["id_azienda"],
                co2_compensata=co2, nome_azione=descrizione
            )
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)

    def get_prodotti_standard(self) -> list[ProductStandardModel]:
        try:
            role = Session().current_user["role"]
            if role == "Agricola":
                return self.product.get_prodotti_standard_agricoli()
            if role == "Trasformatore":
                return self.product.get_prodotti_standard_trasformazione()
            raise TypeError(f"Utente {role} non autorizzato per ottenere prodotti standard")
        except Exception as e:
            logger.error(f"Errore nel ottenimento dei prodotti standard: {e}", exc_info=True)
            return []

    def get_richieste_ric_token(self) -> list[RichiestaTokenModel]:
        try:
            return self.richieste.get_richieste_ric_token(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)
            return []
        
    def get_richiesta_inv_token(self) -> list[RichiestaTokenModel]:
        try:
            return self.richieste.get_richiesta_inviata_token(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)
            return []
        
    def get_operazioni_token(self) -> list[RichiestaTokenModel]:
        try:
            return self.richieste.get_operazioni_token(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)
            return []
        
    def update_richiesta_token(self, richiesta: RichiestaTokenModel, stato: str):
        try:
            self.richieste.update_richiesta_token(richiesta, stato)
        except ValueError as e:
            logger.error(f"Errore {e}", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)

    def send_richiesta_token(self, id_azienda_ricevente: int, quantita: int):
        try:
            self.richieste.send_richiesta_token(Session().current_user["id_azienda"],id_azienda_ricevente, quantita)
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)

    def get_aziende(self) -> list[CompanyModel]:
        try:
            return self.company.get_lista_aziende(escludi_azienda=Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)
            return []
        