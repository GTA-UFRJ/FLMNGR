import configparser
from threading import Thread, Lock

import pika

fd = open("events.json", "w")
fd.write("[\n")

writeLock = Lock()


class WorkerThread(Thread):
    def __init__(self, host, port):
        super(WorkerThread, self).__init__()
        self._is_interrupted = False
        self._conn_params = pika.ConnectionParameters(host, port)

    def stop(self):
        self._is_interrupted = True

    def run(self):
        connection = pika.BlockingConnection(self._conn_params)
        channel = connection.channel()
        channel.queue_declare("events")
        for message in channel.consume("events", inactivity_timeout=1):
            if self._is_interrupted:
                break
            if not all(message):
                continue
            method, _, body = message
            writeLock.acquire()
            print(f"event received: {body.decode('utf-8')}")
            fd.write(f"\t{body.decode('utf-8')},\n")
            writeLock.release()
            channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    print("Starting consumers...")
    configs = configparser.ConfigParser()
    configs.read("./config.ini")

    a = WorkerThread(configs["server.broker"]["host"], configs["server.broker"]["port"])
    b = WorkerThread(configs["client.broker"]["host"], configs["client.broker"]["port"])

    a.start()
    b.start()

    try:
        print("Started consuming....")
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping listener...")
        a.stop()
        b.stop()
    except Exception as err:
        print(f"Error: {str(err)}")
        print("Stopping listener...")
        a.stop()
        b.stop()

    print("Saving file")
    fd.write("]")
    fd.close()
