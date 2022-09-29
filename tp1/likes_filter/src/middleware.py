from common.middleware import Middleware

DISTRIBUTION_EXCHANGE = 'distribution_exchange'
FILTERED_LIKES_EXCHANGE = 'filtered_exchange'


class LikesFilterMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.exchange_declare(exchange=FILTERED_LIKES_EXCHANGE,
                                      exchange_type='fanout')

        result = self.channel.queue_declare(queue='', exclusive=True)

        self.input_queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=self.input_queue_name)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.input_queue_name, lambda ch, method,
                                                properties, body: callback(body.decode()))
        self.channel.start_consuming()

    def send_video_message(self, message):
        super().send_to_exchange(FILTERED_LIKES_EXCHANGE, message)
