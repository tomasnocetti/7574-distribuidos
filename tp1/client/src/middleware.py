import logging
import os
import pika

from common.middleware import Middleware

RAW_DATA_QUEUE = 'raw_data_queue'
CATEGORIES_QUEUE = 'categories_queue'
VIDEO_DATA_QUEUE = 'video_data'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'


class ClientMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(queue=RAW_DATA_QUEUE)
        self.channel.queue_declare(
            queue=CATEGORIES_QUEUE)
        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE)

    def send_category_message(self, message):
        super().send_message(CATEGORIES_QUEUE, message)

    def send_video_message(self, message):
        super().send_message(VIDEO_DATA_QUEUE, message)
