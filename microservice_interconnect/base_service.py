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
    
    :param hide_error_info: if True, internal errors are not forwarded to client
    :type hide_error_info: bool

    :param broker_host: IP or hostname of RPC broker
    :type broker_host: str
    
    :param broker_port: RPC broker port
    :type broker_port: int
    """
    def __init__(
            self, 
            hide_error_info:bool=False, 
            broker_host:str="localhost",
            broker_port:int=5672) -> None:
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.hide_error_info = hide_error_info
        self.func_name_to_func_and_schema_map = {}
        self.background = None

    def add_api_endpoint(self, func_name:str, schema: Dict[str, Any], func: Any):
        """
        Register a new function to be executed uppon receiving RPC call 

        :param func_name: name of the function to be executed
        :type func_name: str

        :param schema: JSON schema
        :type schema: dict

        :param func: function to be executed
        :type func: Any
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
        response = self._process_generic_request(body, func_name=props.type)
        self._send_response(ch, props, method, response)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _process_generic_request(self, body:str, func_name:str) -> str:
        """
        Process received HTTP body, calling corresponding registered function implemented in child

        :param body: HTTP request body
        :type body: str

        :param func_name: name of the function to be executed
        :type func_name: str

        :return: HTTP response body
        :rtype: str
        """
        rcv_data = json.loads(body)
        print(f"Received {func_name} / {rcv_data}")
        
        try:
            func_and_schema = self.func_name_to_func_and_schema_map[func_name]
            if func_and_schema.get("schema") is not None:
                jsonschema.validate(instance=rcv_data, schema=func_and_schema.get("schema"))
            response = self._try_exec_child_func_and_build_response(func_and_schema.get("func"), rcv_data)
        
        except KeyError as e:
            response = {
                'status_code': 500,
                'exception': f"{func_name} is an invalid RPC function"
            }

        except jsonschema.ValidationError as e: 
            response = {
                'status_code': 400,
                'exception': f"{func_name} cannot be executed due to invalid arguments: {e}"
            }
        
        except Exception as e:
            if self.hide_error_info:
                response = {'status_code': 500,'exception': f"{func_name} Internal error"}
            else:
                response = {'status_code': 500,'exception': f"{func_name} An unknown error occured: {e}"}


        print(f"Response: {response}")
        return json.dumps(response)

    def _try_exec_child_func_and_build_response(self, func, argument):
        try:
            returned = func(argument)
            return {"status_code":200,"return":returned}
        except Exception as e:
            if self.hide_error_info:
                return {"status_code":500,"exception":"Internal error"}
            else:
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
        """
        Start listening to queues for RPC requests. Each queue corresponds to a function beeing called

        NOTE: background = True is not recommended because of lack of testing 

        :param background: if True, a thread will be created and the function will be non-blocking 
        :type background: bool
        """
        self.connection = pika.SelectConnection(
            pika.ConnectionParameters(
                host=self.broker_host, 
                port=self.broker_port),
            on_open_callback=self._on_open
        )

        print("Starting service...")
        if background:
            self.background = True
            self.service_thread = threading.Thread(target=self.connection.ioloop.start)
            self.service_thread.start()
        else:
            self.background = False
            self.connection.ioloop.start()

    def stop(self):
        """
        Stops the microsservice from listing to RPC queues
        """
        if self.background is None:
            return
        elif self.background is False:
            self.connection.close()
        else: # self.background is True
            self.connection.close()
            self.service_thread.join()