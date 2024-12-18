
from microservice_interconnect.rpc_client import rpc_send
from pprint import pprint

response = rpc_send("rpc_exec_a", {"arg_1":3,"arg_2":"whatever"})
pprint(response)
input("press enter...")

response = rpc_send("rpc_exec_a", {"arg_1":"aaaaaa","arg_2":""})
pprint(response)
input("press enter...")

response = rpc_send("rpc_exec_a_bug", {"arg_1":3})
pprint(response)
input("press enter...")