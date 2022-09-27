from common.middleware import Middleware

CATEGORIES_QUEUE = 'categories_queue'
VIDEO_DATA_QUEUE = 'video_data'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'


class JoinerMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(
            queue=CATEGORIES_QUEUE)
        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE)

        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')

    def stop_recv_category_message(self):
        super().stop_recv_message(self.cat_msg_tag)

    def stop_recv_video_message(self):
        super().stop_recv_message(self.vid_msg_tag)

    def recv_category_message(self, callback):
        self.cat_msg_tag = super().recv_message(CATEGORIES_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()))

        self.channel.start_consuming()

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(VIDEO_DATA_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()))

    def send_video_message(self, message):
        super().send_to_exchange(DISTRIBUTION_EXCHANGE, message)
