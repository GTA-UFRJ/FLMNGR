sudo docker run --hostname broker -d --rm --name server-broker-rabbit -p 9000:5672 rabbitmq:3 
sudo docker run --hostname broker -d --rm --name client-broker-rabbit -p 8000:5672 rabbitmq:3
