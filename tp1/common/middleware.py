import os
import pika


class Middleware():
    def __init__(self) -> None:
        host = os.environ['RABBIT_SERVER_ADDRESS']

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host))

        self.channel = self.connection.channel()

    def send_message(self, queue, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=message)

    def stop_recv_message(self, consumer_tag):
        self.channel.basic_cancel(consumer_tag=consumer_tag)

    def recv_message(self, queue, callback):
        return self.channel.basic_consume(queue, callback, auto_ack=True)

    def close_connection(self):
        self.connection.close()
