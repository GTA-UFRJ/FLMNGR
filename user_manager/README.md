
# User Manager

This microservice is responsible for CRUD operation on user database

### Test User Manager service

For testing the service with RabbitMQ broker, run:

```shell
docker stop broker-rabbit
docker rm broker-rabbit
docker run -d --hostname broker --name broker-rabbit -p 5672:5672 rabbitmq:3
python -m test_user_manager_logic
```