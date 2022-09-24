import logging
import os
import pika

RAW_DATA_QUEUE = 'raw_data_queue'
CATEGORIES_QUEUE = 'categories_queue'


class Middleware():
    def __init__(self) -> None:
        host = os.environ['RABBIT_SERVER_ADDRESS']

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host))

        self.channel = self.connection.channel()

        self.raw_data_queue = self.channel.queue_declare(queue=RAW_DATA_QUEUE)
        self.categories_queue = self.channel.queue_declare(
            queue=CATEGORIES_QUEUE)

    def __send_message(self, queue, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=message)

    def send_category_message(self, message):
        self.__send_message(CATEGORIES_QUEUE, message)

    # def get_message(self, queue, callback):
    #     self.channel.basic_consume(queue, callback, auto_ack=True)

    def close_connection(self):
        self.connection.close()
