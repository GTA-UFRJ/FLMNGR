import pika
import uuid
import json
import time as tm

class RpcClient:
    """
    Implements an RPC client for microservices communication using a Pika connection to the channel

    :param queue_name: destination function name to send the call
    :type queue_name: str  

    :param host: IP or hostname of destination broker 
    :type host: str  

    :param port: broker port
    :type port: int

    :raises pika.exceptions.AMQPConnectionError: broker inaccessible
    """
    def __init__(self, queue_name:str=None, host:str="localhost", port:int=5672) -> None:

        self._connection_params = pika.ConnectionParameters(host=host, heartbeat=600, port=port)
        self._connection = None
        self._channel = None
        self.queue_name = queue_name

        # Makes the connection in a separate method so it can be called later
        self._connect()

        self.response = None
        self.corr_id = None

    def _connect(self):
        self._connection = pika.BlockingConnection(self._connection_params)
        self._channel = self._connection.channel()

    def _on_response(self, ch, method, props, body) -> None:
        if self.corr_id == props.correlation_id:
            self.response = body

    def _publish(self, data:dict, properties=None):
        if not properties:
            properties = pika.BasicProperties(content_type="text/plain")

        self._channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            properties=properties,
            body=json.dumps(data),
        )

    def publish(self, data:dict, properties=None):
        """
        Sends a message without waiting for a response
        It attempts to reconnect if the connection was closed for any reason before raising exception

        :param data: JSON data to be sent
        :type data: dict

        :param properties: Pika message properties
        :type properties: pika.BasicProperties
        """
        if properties is None:
            properties = pika.BasicProperties(
                content_type="text/plain"
            )
        
        # This queue probabily alerdy exists, but its nice to declare
        self._channel.queue_declare(queue=self.queue_name, exclusive=False)

        while True:
            try:
                self._publish(data, properties)
                return
            except pika.exceptions.ConnectionClosedByBroker as e:
                print("ERROR: Connection closed by broker")
                raise e
            except pika.exceptions.AMQPChannelError:
                print("ERROR: AMQP channel error")
                raise e
            except pika.exceptions.AMQPConnectionError:
                self._connect()

    def _prepare_callback(self):
        callback_queue = self._channel.queue_declare(queue="", exclusive=True)
        self.callback_queue_name = callback_queue.method.queue

        self._channel.basic_consume(
            queue=self.callback_queue_name,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

    def call(self, data: dict) -> dict:
        """
        Sends a message to a microservice and waits for a response

        :param data: JSON data to be sent to the microservice
        :type data: dict

        :return: JSON microservice response from callback queue
        :rtype: dict
        """
        self._prepare_callback()

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.publish(
            data,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue_name,
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


def _publish_event(data, host:str="localhost", port:int=5672):
    rpc_client = RpcClient(queue_name="events", host=host, port=port)
    rpc_client.publish(data)

def rpc_send(func_name:str, request:dict, host:str="localhost", port:int=5672) -> dict:
    """
    Used to call a function in other microsservice and wait for the response

    :param func_name: function name in the destination
    :type func_name: str

    :param request: parameters in JSON format
    :type request: dict

    :param host: broker IP or hostname
    :type host: str
    
    :param port: broker port
    :type port: int

    :return: JSON with funtion return
    :rtype: dict
    """
    rpc_client = RpcClient(queue_name=func_name, host=host, port=port)
    print(f"Sent {func_name} / {request}")
    response = rpc_client.call(request)
    print(f"Received {response}")
    return response

def register_event(
        service_name:str, 
        func_name:str, 
        event_descr:str, 
        allow_registering:bool=True,
        host:str="localhost", 
        port:int=5672
    ):
    """
    Used to register the occurence of an action in a microservice for logging
    
    :param service_name: identifies the origin that registered the event
    :type service_name: str
    
    :param func_name: identifies the function name where the event happened
    :type func_name: str
    
    :param event_descr: identifies and describes the event itself with a short text
    :type event_descr: str

    :param allow_registering: if False, will do nothing. Used for turning off logging
    :type allow_registering: bool

    :param host: broker IP or hostname
    :type host: str
    
    :param port: broker port
    :type port: int
    """
    
    if allow_registering:
        _publish_event(
            {
                "time": tm.time(),
                "service": service_name,
                "function": func_name,
                "event": event_descr,
            },
            host,
            port,
        )
