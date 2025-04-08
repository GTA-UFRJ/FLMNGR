# Tutorial

The purpose of this artifact is to exemplify the use of the AGATA tool through an example and two experiments:

* The basic example involves manually initializing microservices and starting a task via a web interface.

* The first experiment initializes the server's microservices and then creates and initializes a simple learning task on the server, executed on the local machine. Then, the client microservices are initialized on the same machine, automatically transferring the task to the client.

* The second experiment differs from the first by initializing one task with an error (E) and another correct one (C). When an error occurs in E, the client automatically switches the task to C.


## Basic Information

The experiments were conducted on different physical and virtual machines with the following specifications:
* VM with 4 CPUs, 8GB RAM, and Debian 12, instantiated on a server with an Intel Xeon E5-2650 CPU, 8 cores, and 16 threads, 2.80GHz, and 32GB RAM.
* PC with Intel i9-10900, 2.80 GHz CPU, 20 threads, 32GB RAM, and Ubuntu 20.04.

Since no performance issues were observed in any of these configurations, execution is assumed to be guaranteed under the following conditions:
* Operating System: Ubuntu 20.04 or Debian 12
* Minimum CPU: Intel i5 8th Generation
* Minimum RAM: 8GB

## Dependencies

The requirements are:
* Python 3.12.7
* Conda (miniconda3)
* Docker 24.0.7

## Installation

The following tutorial presents the manual initialization of microservices. Executing these commands manually, without an automated script, provides a clearer understanding of AGATA's architecture. However, more automated scripts have been provided for running subsequent experiments, greatly simplifying the installation process. All commands must be executed from the root of the repository.

### New Conda Environment

Create a Conda environment:

```bash
conda create -n agata python=3.12.7
```

Activate the Conda environment for the first time:

```bash
conda activate agata
```

Install dependencies within the Conda environment:

```bash
conda install pip
pip install -r requirements.txt
```

### Configuration File

The `config.ini` file should be configured as follows:

```ini
[client.broker]
host=localhost
port=8000

[server.broker]
host=localhost
port=9000

[server.gateway]
port=9001

[events]
register_events=false

[client.params]
request_interval=10
```

### Server Initialization

#### Start the Broker

Before executing the command, check if a container named `server-broker-rabbit` exists using `docker ps`. If it does, stop and remove it with:

```bash
sudo docker stop server-broker-rabbit
sudo docker rm server-broker-rabbit
```

The broker will listen on port 9000 of the host. Ensure no other application is using this port, then execute:

```bash
sudo docker run -d --hostname broker --rm --name server-broker-rabbit -p 9000:5672 rabbitmq:3
```

#### Start the Cloud Gateway

Open a new terminal, activate the environment (`conda activate agata`), and run:

```bash
python3 -u -m cloud_gateway.http_gateway
```

#### Start the User Manager

Open a new terminal, activate the environment (`conda activate agata`). Before executing the command below, delete the file `user_manager/db/users.db` if it exists. Then execute:

```bash
python3 -u -m user_manager.service_user_manager
```

#### Start the Cloud Task Manager

Open a new terminal, activate the environment (`conda activate agata`). Before executing the command below, delete the file `cloud_task_manager/db/tasks.db` if it exists. Then execute:

```bash
python3 -u -m cloud_task_manager.service_cloud_ml
```

#### Start the Task Manager Download Server

Open a new terminal, activate the environment (`conda activate agata`), and execute:

```bash
python3 -u -m cloud_task_manager.host_tasks $(pwd)/cloud_task_manager
```

### Client Initialization

#### Start the Broker

Before executing the command, check if a container named `client-broker-rabbit` exists using `docker ps`. If it does, stop and remove it with:

```bash
sudo docker stop client-broker-rabbit
sudo docker rm client-broker-rabbit
```

The broker will listen on port 8000 of the host. Ensure no other application is using this port, then execute:

```bash
sudo docker run -d --hostname broker --rm --name client-broker-rabbit -p 8000:5672 rabbitmq:3
```

#### Start the Client Gateway

Open a new terminal, activate the environment (`conda activate agata`), and execute:

```bash
python3 -u -m client_gateway.amqp_gateway
```

#### Start the Client Task Manager

Open a new terminal, activate the environment (`conda activate agata`). This is the **client task manager**, not the one previously started on the server. Before executing the command below, delete all files inside the directories `client_task_manager/tasks/` and `client_task_manager/client_info/`, if they exist. Do **not** delete the directories themselves. Then execute:

```bash
python3 -u -m client_task_manager.service_client_ml
```

At this point, the client will begin sending requests to the server to:
* Register its information
* Request tasks to download, if available


## Minimum Test

The minimum test depends on manual initialization, as described in the previous section.

### Task Execution

#### Access the Graphical Interface

In a new terminal, run the following command and open the local web browser on port 9999 to access a web interface for interacting with the cloud environment. **Acess the web interafce using http://localhost:9999**

```bash
python3 -m http.server -d cloud_web_interface 9999
```

#### Register the Task

Click on the `Create task` link and fill in the form fields as shown in the image below.

After clicking `Submit`, the cloud task manager will register a new task in its database. The files for this task are located in `cloud_task_manager/tasks/task_4fe5/*`. The file upload could be done by accessing the `Upload task files` option in the main menu, but this step was omitted for simplicity.

![alt text](create_task_2.png)

#### Start the Task on the Server

In the main menu, click on the `Start task` link, provide the previously added ID (`4fe5`), and leave the arguments field empty. Upon submitting the form, the task should start in the cloud task manager. At this point, the client task manager should download the task and start it.

#### Start a Second Test Client

The task server is configured to require at least two clients to progress through rounds. Therefore, we will start a new Flower process directly.
Open a new terminal, activate the environment (`conda activate agata`), and run:

```bash
python3 -u -m cloud_task_manager.tasks.task_4fe5.client cli
```

The task should progress through only one round. Once completed, it should be noted that the task automatically becomes inactive on both the client and server, and it can be triggered again via the task start interface.

### Completion

After the minimum test, services can be stopped (Ctrl + C), as well as brokers (`docker stop [container_name] ; docker rm [container_name]`). The environment can be deactivated (`conda deactivate`).

## Experiments

The experiments are executed using automated scripts. Before running the first experiment, ensure that any Python processes previously started in this artifact are terminated. Do not worry, as containers will be stopped and databases will be deleted by the experiment scripts. The most important thing is that no Python microservice is running to avoid network port conflicts, for example.

### Configuration Modifications

Modify the following line in the `config.ini` file:

```ini
[events]
register_events=true
```

In both cases, the results are presented in the files `experiments/events.json`, `experiments/exp_*_raw_times`, and `logs_*/*`

### Experiment 1

To run the first experiment, described at the beginning of this artifact, execute:

```bash
conda activate agata
bash experiments/exp1.sh
```

Superuser permission will be required to run Docker. The experiment takes approximately 4 minutes. The reviewer can follow the progress of the experiment in the terminal. Details about the experiment are found in the article. Task registration and initialization occur via command line instead of a graphical interface. The most relevant results are:
* The `experiments/events.json` file presents, in execution order, the main steps required for executing the federated learning task, along with the corresponding timestamp and component where they occur.
* The `experiments/exp1_raw_times` file summarizes the time taken for the most important operations.

### Experiment 2

To run the second experiment, described at the beginning of this artifact, execute:

```bash
conda activate agata
bash experiments/exp2.sh
```

Similarly, observe the files `experiments/events.json` and `experiments/exp2_raw_times`.
