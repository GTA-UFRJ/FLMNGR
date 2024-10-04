from typing import List, Tuple

import flwr as fl
import argparse
from flwr.server.client_manager import SimpleClientManager 
from flwr.server.client_proxy import ClientProxy
from flwr.common import Metrics

from pathlib import Path

def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    return {"accuracy": sum(accuracies) / sum(examples)}


strategy = fl.server.strategy.FedAvg(
    evaluate_metrics_aggregation_fn=weighted_average)

certs = (
    Path("./certificates/ca.crt").read_bytes(),
    Path("./certificates/server.pem").read_bytes(),
    Path("./certificates/server.key").read_bytes(),
)

# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:7777",  
    config=fl.server.ServerConfig(num_rounds=25),
    strategy=strategy,
    certificates=certs
)
