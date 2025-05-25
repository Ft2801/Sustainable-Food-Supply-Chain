from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eth_account.messages import encode_defunct
from eth_account import Account
import os
import socket
import json

from web3 import Web3
from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.controller.blockchain_controller import BlockchainController

# Ottieni il percorso assoluto della directory corrente (dove si trova questo file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app) 

esiti_operazioni = {}

@app.route("/firma.html")
def firma_html():
    return send_from_directory(BASE_DIR, "firma.html")

@app.route("/verifica", methods=["POST"])
def verifica():
    data = request.json
    print("Dati ricevuti:", data)  # Debug dei dati

    try:
        # Verifica che tutti i campi necessari siano presenti
        required_fields = ["message", "signature", "address", "tipo", "indirizzo", "username", "password"]
        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"Campo mancante: {field}"}), 400

        message = data["message"]
        signature = data["signature"]
        address = data["address"]
        tipo = data["tipo"]
        indirizzo = data["indirizzo"]
        username = data["username"]
        password = data["password"]

        # Verifica della firma
        eth_message = encode_defunct(text=message)
        recovered = Account.recover_message(eth_message, signature=signature)

        if recovered.lower() != address.lower():
            return jsonify({"message": "Firma non valida"}), 400
        
        # Registrazione dell'azienda
        controller = ControllerAutenticazione()
        success = controller.registrazione(
            username=username,
            password=password,
            tipo=tipo,
            indirizzo=indirizzo,
            blockchain_address=address
        )

        if not success:
            return jsonify({"message": "Errore nella registrazione"}), 400

        return jsonify({
            "message": "Registrazione completata con successo!",
            "address": address
        })
        
    except Exception as e:
        print("Errore durante la verifica:", str(e))  # Debug dell'errore
        return jsonify({"message": f"Errore nella registrazione: {str(e)}"}), 400
    

@app.route("/firma_operazione.html")
def firma_operazione_html():
    return send_from_directory(BASE_DIR, "firma_operazione.html")
  # chiave: address, valore: esito str (successo o errore)

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

        esiti_operazioni[address][id_operazione] = f"✅ Operazione registrata con successo. Tx hash: {tx_hash}"
        return jsonify({"message": esiti_operazioni[address][id_operazione]})

    except Exception as e:
        esiti_operazioni[address][id_operazione] = f"❌ Errore: {str(e)}"
        return jsonify({"message": esiti_operazioni[address][id_operazione]}), 400
    
@app.route("/firma_azione.html")
def firma_azione_html():
    return send_from_directory(BASE_DIR, "firma_azione.html")

@app.route("/conferma_azione", methods=["POST"])
def conferma_azione():
    data = request.json
    try:
        address = data["address"]
        messaggio = data["messaggio"]
        signature = data["signature"]

        tipo = data["tipo"]
        co2 = data["co2"]
        data_azione = data["data"]

        print(f"Messaggio ricevuto: {messaggio}")
        
        try:            
            print(f"Parametri estratti: tipo={tipo}, co2={co2}, data={data_azione}")
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
        tx_hash = controller.invia_azione(
            tipo_azione=tipo,
            description=messaggio,
            data_azione=data_azione,
            co2_compensata=co2,            
            account_address=address
        )

        esiti_operazioni[Web3.to_checksum_address(address)] = f"✅ Azione Compensativa registrata con successo. Tx hash: {tx_hash}"
        return jsonify({"message": esiti_operazioni[address]})

    except Exception as e:
        esiti_operazioni[address] = f"❌ Errore: {str(e)}"
        return jsonify({"message": esiti_operazioni[address]}), 400




@app.route("/esito_operazione/<address>/<int:id_operazione>", methods=["GET"])
def esito_operazione(address, id_operazione):
    for account in esiti_operazioni:
        if account == address:
            esito = account.get(id_operazione)
            return jsonify({"status": "completed", "esito": esito}), 200

    return jsonify({"status": "pending"}), 202




if __name__ == "__main__":
    app.run(port=5001)
