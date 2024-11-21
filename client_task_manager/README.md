
# Cloud Task Manager

This microservice is responsible for:
* Periodically providing local client statistics for the cloud
* Periodically requesting available compatible tasks to the cloud
* Downloading client codes for training received tasks
* Starting and stopping Flower training services at the client in real time
* Logging Flower process information and errors (NOT YET IMPLEMENTED)

For more information about Flower Tasks Daemon Library (FTDL), read Cloud Task Manager README file

### Test Client Task Manager service

Client Task Manager is a component that receives messages through a RabbitMQ
broker for RPC function execution. This broker logic is not yet implemented. 
The responsability of this service is to manage client tasks being started
and finished. 

```
python -m test_client_ml_logic
```