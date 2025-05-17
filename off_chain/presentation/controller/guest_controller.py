# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from configuration.log_load_setting import logger
from model.company_model import CompanyModel
from model.product_model import ProductModel
from model.prodotto_finito_cliente import ProdottoFinito
from model.certification_model import CertificationModel
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl
from persistence.repository_impl.database_standard import aziende_enum


class ControllerGuest:
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
        logger.info(
            "BackEnd: Successful initialization of 'class instances' for repository implements")

    def lista_rivenditori(self)-> list[CompanyModel]:
        rivenditori = self.company.get_lista_aziende(tipo= aziende_enum.RIVENDIORE)
        return rivenditori

    # Restituisce la lista di tutte le aziende
    def lista_aziende(self) -> list[CompanyModel]:
        lista_aziende = self.company.get_lista_aziende()
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per tipo
    def lista_aziende_filtro_tipo(self, tipo_azienda : aziende_enum) -> list[CompanyModel]:
        
        lista_aziende = self.company.get_lista_aziende(tipo = tipo_azienda)
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per nome (unica azienda)
    def azienda_by_nome(self, nome_azienda)-> CompanyModel:
        
        azienda = self.company.get_lista_aziende(nome = nome_azienda)
        return azienda

    # Restituisce la lista di tutti i prodotti finali
    def lista_prodotti(self):
        # repo6 = ProductRepositoryImpl()
        lista_prodotti = self.product.get_lista_prodotti()
        return lista_prodotti

    def is_certificato(self, id_prodotto):

        # return self.certification.is_certificato(id_prodotto)
        try:
            certificazione = self.certification.is_certificato(id_prodotto)
            return certificazione
        except Exception as e:
            logger.error(f"Errore durante il recupero della certificazione per il prodotto {id_prodotto}: {str(e)}")
            return None  # O gestire l'errore in un altro modo, come ritornare un messaggio d'errore



    def certificazione_by_prodotto(self, id_prodotto):
        # repo16 = CertificationRepositoryImpl()
        try:
            certificazione = self.certification.get_certificazione_by_prodotto(id_prodotto)
            return certificazione
        except Exception as e:
            logger.error(f"Errore durante il recupero della certificazione per il prodotto {id_prodotto}: {str(e)}")
            return None  # O gestire l'errore in un altro modo, come ritornare un messaggio d'errore

 

    # Restituisce lo scarto dalla soglia di riferimento

    def scarto_soglia(self, co2, operazione, prodotto):
        # repo17 = ThresholdRepositoryImpl()
        soglia = self.threshold.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
    

    def carica_prodotto_con_storia(self, prodotto_id : int) -> ProductModel:
        """
        Carica un prodotto con la sua storia a partire dal suo ID.
        """
        try:
            prodotto = self.get_fake_prodotto(prodotto_id)
            return prodotto
        except Exception as e:
            logger.error(f"Errore durante il caricamento del prodotto con ID {prodotto_id}: {str(e)}")
            return None

    def get_prodotti(self) -> list[ProdottoFinito]:
        try:
            return self.product.get_lista_prodotti()
        except Exception as e:
            logger.error(f"Errore durante il recupero dei prodotti: {str(e)}")
            return []
            
    def get_certificazioni_by_lotto(self,lotto_id : int)-> list[CertificationModel]:
        try:
            return self.certification.get_certificati_catena(lotto_id) or []
        except Exception as e:
            logger.error(f"Errore nel recuperare i certificai {e}")
        