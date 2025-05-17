# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
# pylint: disable= C0103 # Ignora gli errori di nome variabile/metodo come richiesto
from configuration.log_load_setting import logger
from model.lotto_for_cetification_model import LottoForCertificaion
from model.certification_for_lotto import CertificationForLotto
from session import Session
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl


class ControllerCertificatore:
    """
    As the instance has been created, in the repository implement layer, to access your methods,
    we initialize the instances of the classes 'class instances' with:
            CertificationRepositoryImpl()
            ProductRepositoryImpl()
            ThresholdRepositoryImpl()
            CompanyRepositoryImpl()
            get_certifications_by_product_interface
    """

    def __init__(self):
        self.certification = CertificationRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")

    # Restituisce il dettaglio dell'azienda selezionata dato l'indice n
    def get_dettaglio_azienda(self, id_azienda):
        # repo = CertificationRepositoryImpl()
        return self.certification.get_numero_certificazioni(id_azienda)

    def certificazione_by_prodotto(self, id_prodotto):
        # repo = CertificationRepositoryImpl()
        certificazione = self.certification.get_certificazione_by_prodotto(id_prodotto)
        return certificazione

    def inserisci_certificato(self, id_prodotto, descrizione, id_azienda_certificatore, data):
        # repo = CertificationRepositoryImpl()
        self.certification.inserisci_certificato(id_prodotto, descrizione, id_azienda_certificatore, data)

    # Restituisce la lista di tutti i prodotti finali
    def lista_prodotti(self):
        # repo = ProductRepositoryImpl()
        lista_prodotti = self.product.get_lista_prodotti()
        return lista_prodotti


    def get_lotti_certificabili(self) -> list[LottoForCertificaion]:
        try:
            return self.certification.get_lotti_certificabili()
        except Exception as e:
            logger.error(f"Errore nel recupero dei lotti: {e}", exc_info=True)
            return [] # R1710: Ritorna lista vuota in caso di errore

    def get_certificati_lotto(self, id_lotto: int) -> list[CertificationForLotto]:
        try:
            return self.certification.get_certificati_lotto(id_lotto)
        except Exception as e:
            logger.error(f"Errore nel recupero dei certificati: {e}", exc_info=True)
            return [] # R1710: Ritorna lista vuota in caso di errore

    def aggiungi_certificazione(self, id_lotto, descrizione):
        try:
            self.certification.aggiungi_certificazione(id_lotto, descrizione, Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nel aggiunta dei certificati: {e}", exc_info=True)
