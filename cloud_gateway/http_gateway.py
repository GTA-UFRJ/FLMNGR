import configparser
from flask import Flask, request, jsonify
from flask_cors import CORS  # Importando CORS
from microservice_interconnect.rpc_client import rpc_send, register_event

app = Flask(__name__)
CORS(app)  # Habilitando CORS para todas as rotas

configs = configparser.ConfigParser()
configs.read("./config.ini")

rpc_hostname = configs["server.broker"]["host"]
rpc_port = int(configs["server.broker"]["port"])
allow_register = configs.getboolean("events", "register_events")

@app.route("/<function_name>", methods=["POST", "OPTIONS"])
def rpc_handler(function_name):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    register_event("cloud_gateway", "rpc_handler", f"Started redirecting {function_name} msg",
                   allow_registering=allow_register, host=rpc_hostname, port=rpc_port)

    try:
        args = request.get_json()
        if args is None:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        rpc_response = rpc_send(function_name, args, rpc_hostname, rpc_port)
        status_code = rpc_response.get("status_code", 500)

        response_data = rpc_response.get("return") if status_code == 200 else rpc_response.get("exception")

        register_event("cloud_gateway", "rpc_handler", f"Finished redirecting {function_name} msg",
                       allow_registering=allow_register, host=rpc_hostname, port=rpc_port)

        return jsonify(response_data), status_code

    except Exception as e:
        return jsonify({"status_code": 500, "exception": str(e)}), 500

def _build_cors_preflight_response():
    """Retorna a resposta para requisições OPTIONS (CORS Preflight)."""
    response = jsonify({"message": "CORS preflight response"})
    response.headers.add("Access-Control-Allow-Origin", "*")  # Permite qualquer origem
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")  # Métodos permitidos
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")  # Headers permitidos
    return response

if __name__ == "__main__":
    app.run(port=int(configs["server.gateway"]["port"]), debug=True)
