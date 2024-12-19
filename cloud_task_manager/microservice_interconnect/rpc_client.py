import pika
import uuid
import json


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


@singleton
class RpcClient:
    """
    Implements an RPC client for microservices communication using a
    Pika connection to the channel
    """

    def __init__(self, func_name: str, host="localhost", port=5672) -> None:
        """
        Initializes RPC client with a destination queue

        :param queue_name: destination function name
        """
        self.queue_name = func_name

        self._connection_params = pika.ConnectionParameters(host=host, port=port)
        self._connection = None
        self._channel = None

        # Makes the connection in a separate method so it can be called later
        self.connect()

        self.response = None
        self.corr_id = None

    def connect(self):
        # Reconnects whenever connection is closed
        if not self._connection or self._connection.is_closed:
            self._connection = pika.BlockingConnection()

            self._channel = self._connection.channel()

            result = self._channel.queue_declare(queue="", exclusive=True)
            self.callback_queue = result.method.queue

            self._channel.basic_consume(
                queue=self.callback_queue,
                on_message_callback=self._on_response,
                auto_ack=True,
            )

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

    def _publish(self, data, properties=None):
        """
        Function that publishes the message itself. Called by publish function
        """
        if not properties:
            properties = pika.BasicProperties()

        self._channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            properties=properties,
            body=json.dumps(data),
        )

    def publish(self, data, properties=None):
        """
        Sends a message without waiting for a response
        It attempts to reconnect if the connection was closed for any reason before raising exception

        :param data: data to be sent

        :return: None
        """
        try:
            self._publish(data, properties)
        except pika.exceptions.ConnectionClosed:
            self.connect()
            self._publish(data, properties)

    def call(self, data: dict) -> dict:
        """
        Sends a message to a microservice and waits for a response

        :param data: data to be sent to the microservice

        :return: microservice response
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.publish(
            data,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                type=self.queue_name,
            ),
        )
        while self.response is None:
            self._connection.process_data_events()
        response = json.loads(self.response.decode("utf-8"))
        return response

    def close(self) -> None:
        """
        Closes RabbitMQ connection
        """
        self._connection.close()


def publish_event(data, host="localhost", port=5672):
    rpc_client = RpcClient("events", host, port)
    rpc_client.publish(data)


def rpc_send(func_name: str, request: dict, host="localhost", port=5672) -> dict:
    rpc_client = RpcClient(func_name, host, port)
    response = rpc_client.call(request)
    return response
