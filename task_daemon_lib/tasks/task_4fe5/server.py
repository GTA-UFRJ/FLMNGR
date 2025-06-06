import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

if sys.argv[1] != "cli":
    sys.path.append(sys.argv[1])

from typing import List, Tuple

from flwr.common import Metrics, ndarrays_to_parameters
from flwr.server import ServerConfig, start_server
from flwr.server.strategy import FedAvg

from task import Net, get_weights

from task_daemon_lib.task_reporter import TaskReporter
#from task_reporter_temp import TaskReporter

# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    global task_reporter, comm_round
    examples = [num_examples for num_examples, _ in metrics]

    # Multiply accuracy of each client by number of examples used
    train_losses = [num_examples * m["train_loss"] for num_examples, m in metrics]
    train_accuracies = [
        num_examples * m["train_accuracy"] for num_examples, m in metrics
    ]
    val_losses = [num_examples * m["val_loss"] for num_examples, m in metrics]
    val_accuracies = [num_examples * m["val_accuracy"] for num_examples, m in metrics]

    if sys.argv[1] != "cli":
        task_reporter.send_stats(comm_round,metrics)
    else:
        print(metrics)
    comm_round += 1

    acc = sum(val_accuracies) / sum(examples)
    if acc >= 0.5:
        task_reporter.trigger("trigger_example",str(acc))

    #if acc <= 0.6 and comm_round == 10:
    #    rpc_call("rpc_exec_start_tas", ...)

    # Aggregate and return custom metric (weighted average)
    return {
        "train_loss": sum(train_losses) / sum(examples),
        "train_accuracy": sum(train_accuracies) / sum(examples),
        "val_loss": sum(val_losses) / sum(examples),
        "val_accuracy": sum(val_accuracies) / sum(examples),
    }

def get_strategy():
    ndarrays = get_weights(Net())
    parameters = ndarrays_to_parameters(ndarrays)

    return FedAvg(
        fraction_fit=1.0,  # Select all available clients
        fraction_evaluate=1.0,  # Disable evaluation
        min_available_clients=2,
        fit_metrics_aggregation_fn=weighted_average,
        initial_parameters=parameters,
    )

if __name__ == "__main__":

    try:
        if sys.argv[1] != "cli":
            task_reporter = TaskReporter()

        comm_round = 1

        config = ServerConfig(num_rounds=5)

        if len(sys.argv) >= 3:
            if sys.argv[2] == "test-error":
                raise Exception

        start_server(
            server_address="0.0.0.0:8080",
            config=config,
            strategy=get_strategy(),
        )

        if sys.argv[1] != "cli":
            task_reporter.send_info("Finished")

    except Exception as e:
        if sys.argv[1] == "cli":
            raise e
        task_reporter.send_error(e)

