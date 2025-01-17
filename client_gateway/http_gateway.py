import configparser

from flask import Flask, request, jsonify
from microservice_interconnect.rpc_client import rpc_send
from microservice_interconnect.rpc_client import register_event

app = Flask(__name__)

configs = configparser.ConfigParser()
configs.read("./config.ini")

rpc_hostname = configs["client.broker"]["host"]
rpc_port = int(configs["client.broker"]["port"])

allow_register = configs.getboolean("events","register_events")


@app.route("/<function_name>", methods=["POST"])
def rpc_handler(function_name):
    register_event("client_gateway","rpc_handler",f"Started redirecting {function_name} msg",allow_registering=allow_register,host=rpc_hostname,port=rpc_port)

    try:
        # Parse the JSON body of the POST request
        args = request.get_json()
        if args is None:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        # Call the rpc_send function with the function name and arguments
        rpc_response = rpc_send(function_name, args, rpc_hostname, rpc_port)

        # Extract the status code from the rpc_send response
        status_code = rpc_response.get("status_code", 500)

        if status_code == 200:
            response_data = rpc_response.get("return")
        else:
            response_data = rpc_response.get("exception")

        register_event("client_gateway","rpc_handler",f"Finished redirecting {function_name} msg",allow_registering=allow_register,host=rpc_hostname,port=rpc_port)

        # Return the JSON response and the corresponding HTTP status code
        return jsonify(response_data), status_code

    except Exception as e:
        # Handle unexpected errors gracefully
        return jsonify({"status_code": 500, "exception": str(e)}), 500


if __name__ == "__main__":
    app.run(port=int(configs["client.gateway"]["port"]), debug=True)
