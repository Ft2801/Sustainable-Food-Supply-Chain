from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eth_account.messages import encode_defunct
from eth_account import Account
import os
import socket
import json
from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.controller.blockchain_controller import BlockchainController

# Ottieni il percorso assoluto della directory corrente (dove si trova questo file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app) 



@app.route("/firma.html")
def firma_html():
    return send_from_directory(BASE_DIR, "firma.html")

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
    return send_from_directory(BASE_DIR, "firma_operazione.html")

esiti_operazioni = {}  # chiave: address, valore: esito str (successo o errore)

@app.route("/conferma_operazione", methods=["POST"])
def conferma_operazione():
    data = request.json
    try:
        address = data["address"]
        messaggio = data["messaggio"]
        signature = data["signature"]

        # Estrai i parametri dal messaggio
        # Formato: "Conferma operazione {tipo} sil lotto {id_lotto} con id op {id_op}"
        print(f"Messaggio ricevuto: {messaggio}")
        
        try:
            # Parse message to extract type, batch and operation IDs
            parts = messaggio.split("lotto ")
            tipo_parts = parts[0].split("operazione ")
            tipo = tipo_parts[1].strip() if len(tipo_parts) > 1 else ""
            
            lotto_op_parts = parts[1].split("con id op")
            batch_id = int(lotto_op_parts[0].strip())
            id_operazione = int(lotto_op_parts[1].strip())
            
            # Map operation type to numeric value (uint8)
            operation_type_map = {
                "Produzione": 0,
                "Trasformazione": 1,
                "Distribuzione": 2,
                "Vendita": 3
            }
            operation_type = operation_type_map.get(tipo, 0)
            
            print(f"Parametri estratti: tipo={operation_type}, batch_id={batch_id}, id_op={id_operazione}")
        except Exception as e:
            error_msg = f"❌ Errore nel parsing del messaggio: {str(e)}"
            print(error_msg)
            esiti_operazioni[address] = error_msg
            return jsonify({"message": esiti_operazioni[address]}), 400

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
            id_operazione=id_operazione,
            account_address=address
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
    app.run(port=5001)
