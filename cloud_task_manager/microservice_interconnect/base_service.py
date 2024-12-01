import pika
import json
import threading
import signal
import jsonschema
from typing import List, Dict, Any

class BaseService:
    """
    Generic service
    Other services are built as child of this one
    Implements registration and queue management for RabbitMQ
    """

    def __init__(self, service_name: str, queue_names: List[str], ip='localhost') -> None:
        """
        Creates the service
        using Pika

        :param registry: service name
        :param registry: list of queues names 
        """
        self.service_name = service_name
        self.queue_names = queue_names
        
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(ip)
        )
        self.channel = self.connection.channel()
        self._is_running = True

        self.func_name_to_schema_map = {}

    def register_api_endpoint(self, func_name:str, schema: Dict[str, Any], func: Any):
        """
        Register a new API function execution uppon receiving certain JSON 

        :param schema: expected JSON schema
        :param func: function to be executed 
        """
        self.func_name_to_func_and_schema_map[func_name] = {
            "schema":schema,
            "func":func
        }

    def _uppon_receiving_message(
        self,
        ch: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        props: pika.spec.BasicProperties,
        body: bytes
    ) -> None:
        """
        Handle incoming RPC requests.

        :param ch: channel
        :param method: communication method
        :param props: message properties
        :param body: message body
        """

        response = self._process_generic_request(body)
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id
            ),
            body=response
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _process_generic_request(self, body: str) -> str:
        """
        Process received HTTP body, calling child processing function

        :param body: HTTP request body as a string

        :return: HTTP response body as a string
        """
        
        response = {
            'status_code': 500,
            'error': "Function not implemented"
        }

        body[""]

        for schema, child_func in zip(self.schemas_list, self.functions_list):
            data = json.loads(body)
            try:
                jsonschema.validate(instance=data, schema=schema)
                response = child_func(data)
            except jsonschema.ValidationError as e: 
                pass
            except Exception as e:
                response = {
                    'status_code': 500,
                    'error': str(e)
                }
        return json.dumps(response)

    def _wait_and_process_requests(self) -> None:
        """
        Start the service
        """
        
        print(f" [x] {self.service_name} awaiting RPC requests")
        try:
            while self._is_running:
                self.connection.process_data_events(time_limit=1)
        except Exception as e:
            print(f"Error during processing: {e}")
        finally:
            if not self.connection.is_closed:
                self.connection.close()

    def _declare_and_consume_queue(self, func_name:str, func, ) -> None:
        """
        Declare and consume the queue wth the name of the function
        """
        self.channel.queue_declare(queue=func_name)
        self.channel.basic_consume(
            queue=func_name,
            on_message_callback=self._uppon_receiving_message,
            auto_ack=False
        )

    def stop(self) -> None:
        """
        Stop the service.
        """
        self._is_running = False
        if not self.connection.is_closed:
            self.connection.close()

    def run(self) -> None:
        """
        Run the service in a separate thread with signal handling.
        """
        service_thread = threading.Thread(target=self._wait_and_process_requests)

        def signal_handler(sig: int, frame: Any) -> None:
            print('Stopping service...')
            self.stop()
            service_thread.join()
            print('Service stopped.')

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self._declare_and_consume_queue()

        service_thread.start()