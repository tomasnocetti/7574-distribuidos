import logging
from common.middleware import Middleware

DROPPER_INPUT_QUEUE = 'dropper_input'
VIDEO_DATA_QUEUE = 'video_data'

logging.getLogger("pika").propagate = False


class DropperMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(
            queue=DROPPER_INPUT_QUEUE)

        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE)
        self.channel.basic_qos(prefetch_count=1)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(DROPPER_INPUT_QUEUE, lambda ch, method,
                                                properties, body:
                                                    self.callback_with_ack(callback, ch, method, properties, body.decode()), False)
        self.channel.start_consuming()

    def callback_with_ack(self, callback, ch, method, properties, body):
        callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_video_message(self, message):
        super().send_message(VIDEO_DATA_QUEUE, message)
