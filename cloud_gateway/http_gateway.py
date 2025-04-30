import configparser
from flask import Flask, request, jsonify
from flask_cors import CORS  
from microservice_interconnect.rpc_client import rpc_send, register_event
from flask.wrappers import Response

app = Flask(__name__)
CORS(app)  

configs = configparser.ConfigParser()
configs.read("./config.ini")

rpc_hostname = configs["server.broker"]["host"]
rpc_port = int(configs["server.broker"]["port"])
allow_register = configs.getboolean("events", "register_events")

@app.route("/<function_name>", methods=["POST", "OPTIONS"])
def rpc_handler(function_name:str)->Response:
    '''
    Forward HTTP request to corresponding queue identified by route/function
    
    :param function_name: RPC function name, specified in the HTTP header
    :type function_name: str

    :return: response
    :rtype: flask.wrappers.Response
    '''
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
    response = jsonify({"message": "CORS preflight response"})
    response.headers.add("Access-Control-Allow-Origin", "*") 
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS") 
    response.headers.add("Access-Control-Allow-Headers", "Content-Type") 
    return response

if __name__ == "__main__":
    app.run(host=configs["server.broker"]["host"], port=int(configs["server.gateway"]["port"]), debug=True)
