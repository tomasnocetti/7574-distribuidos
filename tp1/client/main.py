#!/usr/bin/env python
import time
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitMQ'))
channel = connection.channel()

channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
