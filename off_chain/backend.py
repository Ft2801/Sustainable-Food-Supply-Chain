from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eth_account.messages import encode_defunct
from eth_account import Account
from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.controller.blockchain_controller import BlockchainController


app = Flask(__name__)
CORS(app) 



@app.route("/firma.html")
def firma_html():
    return send_from_directory(".", "firma.html")

@app.route("/verifica", methods=["POST"])
def verifica():
    data = request.json
    print("Dati ricevuti:", data)  # Debug utile

    try:
        message = data["message"]
        signature = data["signature"]
        address = data["address"]

        tipo = data["tipo"]
        indirizzo = data["indirizzo"]
        username = data["username"]
        password = data["password"]

        eth_message = encode_defunct(text=message)
        recovered = Account.recover_message(eth_message, signature=signature)

        if recovered.lower() != address.lower():
            return jsonify({"message": "Firma non valida."}), 400
        
        controller = ControllerAutenticazione()
        controller.registrazione(
            username=username,
            password=password,
            indirizzo=indirizzo,
            tipo=tipo,
            blockchain_address=address
        )

        return jsonify({"message": "Registrazione completata!", "address": address})
    except Exception as e:
        return jsonify({"message": f"Errore nella registrazione: {str(e)}"}), 400
    

@app.route("/firma_operazione.html")
def firma_operazione_html():
    return send_from_directory(".", "firma_operazione.html")

esiti_operazioni = {}  # chiave: address, valore: esito str (successo o errore)

@app.route("/conferma_operazione", methods=["POST"])
def conferma_operazione():
    data = request.json
    try:
        address = data["address"]
        messaggio = data["messaggio"]
        signature = data["signature"]

        operation_type = "Agricola"
        batch_id = "batch_id"  # Placeholder, da sostituire con il valore corretto
        id_operazione = "id_operazione"  # Placeholder, da sostituire con il valore corretto

        # Verifica firma
        eth_message = encode_defunct(text=messaggio)
        recovered_address = Account.recover_message(eth_message, signature=signature)

        if recovered_address.lower() != address.lower():
            esiti_operazioni[address] = "❌ Firma non valida"
            return jsonify({"message": esiti_operazioni[address]}), 400

        # Chiamata al controller per inviare sulla blockchain
        controller = BlockchainController()
        tx_hash = controller.invia_operazione(
            operation_type=operation_type,
            description=messaggio,
            batch_id=batch_id,
            id_operazione=id_operazione
        )

        esiti_operazioni[address] = f"✅ Operazione registrata con successo. Tx hash: {tx_hash}"
        return jsonify({"message": esiti_operazioni[address]})

    except Exception as e:
        esiti_operazioni[address] = f"❌ Errore: {str(e)}"
        return jsonify({"message": esiti_operazioni[address]}), 400


@app.route("/esito_operazione/<address>")
def esito_operazione(address):
    return jsonify({"esito": esiti_operazioni.get(address, "In attesa")})




if __name__ == "__main__":
    app.run(port=5000)
