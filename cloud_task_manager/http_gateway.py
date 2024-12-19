import configparser

from flask import Flask, request, jsonify
from microservice_interconnect.rpc_client import rpc_send

app = Flask(__name__)

configs = configparser.ConfigParser()
configs.read("./config.ini")

rpcHostname = configs["client.broker"]["host"]
rpcPort = int(configs["client.broker"]["port"])


@app.route("/<function_name>", methods=["POST"])
def rpc_handler(function_name):
    try:
        # Parse the JSON body of the POST request
        args = request.get_json()
        if args is None:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        # Call the rpc_send function with the function name and arguments
        rpc_response = rpc_send(function_name, args, rpcHostname, rpcPort)

        # Extract the status code from the rpc_send response
        status_code = rpc_response.get("status_code", 500)

        # Return the JSON response and the corresponding HTTP status code
        return jsonify(rpc_response), status_code

    except Exception as e:
        # Handle unexpected errors gracefully
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=int(configs["server.gateway"]["port"]), debug=True)
