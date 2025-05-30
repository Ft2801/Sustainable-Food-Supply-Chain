from configuration.database import Database

if __name__ == "__main__":

    db = Database()
    query = """
            SELECT *
            FROM ComposizioneLotto
            """
    result = db.fetch_results(query)

    print(result)