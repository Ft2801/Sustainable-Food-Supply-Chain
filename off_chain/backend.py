from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eth_account.messages import encode_defunct
from eth_account import Account
from presentation.controller.credential_controller import ControllerAutenticazione


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


if __name__ == "__main__":
    app.run(port=5000)
