import pika
import uuid
import json

class RpcClient:
    """
    Implements an RPC client for microservices communication using a 
    Pika connection to the channel
    """
    def __init__(self, func_name: str) -> None:
        """
        Initializes RPC client with a destination queue

        :param queue_name: destination function name
        """
        self.queue_name = func_name

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def _on_response(self, ch, method, props, body) -> None:
        """
        Processes a microservice response and verifies if the message is
        the exepected one

        :param ch: channel
        :param method: communication method
        :param props: message properties
        :param body: message body
        """
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data: dict) -> dict:
        """
        Sends a message to a microservice and waits for a response

        :param data: data to be sent to the microservice

        :return: microservice response
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                type=self.queue_name,
            ),
            body=json.dumps(data)
        )
        while self.response is None:
            self.connection.process_data_events()
        response = json.loads(self.response.decode('utf-8'))
        return response

    def close(self) -> None:
        """
        Closes RabbitMQ connection
        """
        self.connection.close()

def rpc_send(func_name:str, request:dict)->dict:
    rpc_client = RpcClient(func_name)
    response = rpc_client.call(request)
    rpc_client.close()
    return response
