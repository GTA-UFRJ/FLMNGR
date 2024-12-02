import pika
import json
import jsonschema
import threading
from typing import Dict, Any

import pika.channel
import pika.spec

class BaseService:
    """
    Generic service
    Other services are built as child of this one
    Implements registration and queue management for RabbitMQ
    """
    def __init__(self) -> None:
        self._is_running = False
        self.func_name_to_func_and_schema_map = {}

    def add_api_endpoint(self, func_name:str, schema: Dict[str, Any], func: Any):
        """
        Register a new API function execution uppon receiving certain JSON 

        :param schema: expected JSON schema
        :param func: function to be executed 
        """
        self.func_name_to_func_and_schema_map[func_name] = {
            "func":func,
            "schema":schema
        }

    def _on_open(self, connection: pika.SelectConnection):
        connection.channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel: pika.channel.Channel):
        for func_name in self.func_name_to_func_and_schema_map.keys():
            channel.queue_declare(queue=func_name)
            channel.basic_consume(
                queue=func_name,
                on_message_callback=self._uppon_receiving_message,
                auto_ack=False
            )

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

        response = self._process_generic_request(body, func_name=props.type)
        self._send_response(ch, props, method, response)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _process_generic_request(self, body:str, func_name:str) -> str:
        """
        Process received HTTP body, calling child processing function

        :param body: HTTP request body as a string

        :return: HTTP response body as a string
        """
        rcv_data = json.loads(body)
        
        try:
            func_and_schema = self.func_name_to_func_and_schema_map[func_name]
            jsonschema.validate(instance=rcv_data, schema=func_and_schema.get("schema"))
            response = self._try_exec_child_func_and_build_response(func_and_schema.get("func"), rcv_data)
        
        except KeyError as e:
            response = {
                'status_code': 500,
                'exception': f"Invalid RPC function: {e}"
            }

        except jsonschema.ValidationError as e: 
            response = {
                'status_code': 400,
                'exception': f"Invalid message: {e}"
            }
        
        except Exception as e:
            response = {
                'status_code': 500,
                'exception': f"An unknown error occured: {e}"
            }
        
        print(f"Response: {response}")
        return json.dumps(response)

    def _try_exec_child_func_and_build_response(self, func, argument):
        try:
            returned = func(argument)
            return {"status_code":200,"return":returned}
        except Exception as e:
            return {"status_code":500,"exception":f"{e}"}

    def _send_response(
        self, 
        ch:pika.channel.Channel, 
        props:pika.spec.BasicProperties, 
        method: pika.spec.Basic.Deliver, 
        response:str
    ):
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id
            ),
            body=response
        )

    def start(self, background:bool=False):

        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(host="localhost"),
            on_open_callback=self._on_open
        )

        if background:
            service_thread = threading.Thread(target=self.connection.ioloop.start)
            service_thread.start()
        else:
            self.connection.ioloop.start()

    def stop(self):
        if not self.connection.is_closed:
            self.connection.close()