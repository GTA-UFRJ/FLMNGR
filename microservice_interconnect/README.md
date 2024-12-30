
# Microservice interconnection library

You must have Docker installed. For testing, run:
```shell
docker stop server-broker-rabbit
docker rm server-broker-rabbit
docker run -d --hostname broker --name server-broker-rabbit -p 5000:5672 

```

Now, run the microservice:
```shell
python -m microservice_interconnect.sample_service
```

Finally, in other terminal, run the tests:
```shell
python -m microservice_interconnect.test_sample_service
```