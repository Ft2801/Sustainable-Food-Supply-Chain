from configuration.database import Database

if __name__ == "__main__":

    db = Database()
    query = """
            SELECT rt.Id_richiesta, rt.Id_richiedente, rt.Id_ricevente, rt.Quantita, rt.Stato, rt.Data,
                   am.Nome as nome_mittente, ad.Nome as nome_destinatario
            FROM RichiestaToken rt
            JOIN Azienda am ON rt.Id_richiedente = am.Id_azienda
            JOIN Azienda ad ON rt.Id_ricevente = ad.Id_azienda
            WHERE rt.Id_richiesta = ?
            """
    result = db.fetch_one(query, (1,))

    print(result)