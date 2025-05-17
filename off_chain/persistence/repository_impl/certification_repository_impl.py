# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from abc import ABC
from configuration.database import Database
from model.certification_model import CertificationModel
from model.lotto_for_cetification_model import LottoForCertificaion
from model.certification_for_lotto import CertificationForLotto
from persistence.query_builder import QueryBuilder
from configuration.log_load_setting import logger


class CertificationRepositoryImpl(ABC):
    """
     Implementing the certificato repository.
     """    


    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
        

    def get_certifications_by_product_interface(self,id_prodotto: int) -> list:

        query = """
        SELECT 
            Certificato.Id_certificato,
            Prodotto.Nome,
            Certificato.Descrizione,
            Azienda.Nome,
            Certificato.Data
        FROM Certificato
        JOIN Azienda ON Certificato.Id_azienda_certificatore = Azienda.Id_azienda
        JOIN Prodotto ON Certificato.Id_prodotto = Prodotto.Id_prodotto
        WHERE Certificato.Id_prodotto = ?;
        """
        query, value = (self.query_builder
                                .select("Certificato.Id_certificato", "Prodotto.Nome","Certificato.Descrizione",
                                        "Azienda.Nome","Certificato.Data"
                                        ).table("Certificato")
                                        .join("Azienda" , "Certificato.Id_azienda_certificatore", "Azienda.Id_azienda")
                                        .join( "Prodotto",  "Certificato.Id_prodotto" , "Prodotto.Id_prodotto")
                                        .where("Certificato.Id_prodotto", "=",id_prodotto)
                                        .get_query()
        )
        
        return self.db.fetch_results(query, value)
         

    def get_numero_certificazioni(self, id_azienda: int) -> int:
        query, values = (
                self.query_builder
                    .table("Certificato")
                    .select("COUNT(*)")
                    .where("Id_azienda_certificatore", "=", id_azienda)
                    .get_query()
        )
        try:
            return int(self.db.fetch_results(query, values)[0])
        except:
            raise ValueError

    def is_certificato(self, id_prodotto: int) -> bool:
        query, value = (
            self.query_builder 
                    .table("Certificato")
                    .select("*")
                    .where("Id_prodotto","=", id_prodotto)
                    .get_query()
        )
        if not self.db.fetch_results(query, value):
            return False
        return True


    # Restituisce la certificazione del prodotto selezionato
    def get_certificazione_by_prodotto(self, prodotto):
        query, values = (
            self.query_builder
                    .select("Certificato.Id_certificato",
                        "Prodotto.Nome",
                        "Certificato.Descrizione",
                        "Azienda.Nome",
                        "Certificato.Data"
                    )
                    .table("Certificato")
                    .join("Azienda", "Certificato.Id_azienda_certificatore", "Azienda.Id_azienda")
                    .join( "Prodotto", "Certificato.Id_prodotto", "Prodotto.Id_prodotto")
                    .where("Certificato.Id_prodotto", "=", prodotto)
                    .get_query()
                    )

        return self.db.fetch_results(query, values)
    

    
    def get_certificati_catena(self, id_lotto: int) -> list[CertificationModel]:
        try:
            certificati: list[CertificationModel] = []

            query, value = (
                self.query_builder
                .select("Id_certificato", "Id_lotto", "Descrizione", "az.Nome", "Data")
                .table("Certificato")
                .join("Azienda AS az", "Id_azienda_certificatore", "az.Id_azienda")
                .where("Id_lotto", "=", id_lotto)
                .get_query()
            )

            result = self.db.fetch_results(query, value)
            certificati.extend([CertificationModel(*r) for r in result])


            lotti_input = self.db.fetch_results("""
                SELECT id_lotto_input FROM ComposizioneLotto WHERE id_lotto_output = ?
            """, (id_lotto,))

            for (id_lotto_input,) in lotti_input:
                certificati.extend(self.get_certificati_catena(id_lotto_input))

            return certificati

        except Exception as e:
            print(f"Errore durante la conversione dei certificati: {e}")
            return []
        

    def get_lotti_certificabili(self) -> list[LottoForCertificaion]:
        try:
            query,value =(
                self.query_builder
                    .select("o.Id_lotto","o.Tipo","o.Data_operazione","o.Consumo_CO2","a.Nome","p.Nome")
                    .table("Operazione AS o")
                    .where("o.Tipo","!=","trasporto")
                    .where("o.Tipo","!=","vendita")
                    .join("Prodotto AS p","o.Id_prodotto","p.Id_prodotto")
                    .join("Azienda AS a","o.Id_azienda","a.Id_azienda")
                    .get_query()
            )

            result = self.db.fetch_results(query,value)
            logger.warning(f"lista {result}")
            return [LottoForCertificaion(*r) for r in result]

        except Exception as e:
            logger.error(f"Errore nel recupero dei lotti: {e}")


    def get_certificati_lotto(self,id_lotto : int) ->list[CertificationForLotto]:
        try:

            query, value = (
                self.query_builder
                .select("Descrizione", "az.Nome", "Data")
                .table("Certificato")
                .join("Azienda AS az", "Id_azienda_certificatore", "az.Id_azienda")
                .where("Id_lotto", "=", id_lotto)
                .get_query()
            )

            result = self.db.fetch_results(query, value)
            if not result:
                logger.warning("Ritorno lista vuota")
            return [CertificationForLotto(*r) for r in result] or []
        except Exception as e:
            logger.error(f"Errore nel recupero dei certificati {e}")

    def aggiungi_certificazione(self,id_lotto, descrizione, id_azienda):
        try:
            query = """INSERT INTO Certificato(Id_lotto,Descrizione,Id_azienda_certificatore) VALUES (?, ?, ?)"""
            value =(id_lotto,descrizione,id_azienda)
            self.db.execute_query(query,value)
        except Exception as e:
            logger.error(f"Errore nel aggiunta del certificato {e}")

            



           



