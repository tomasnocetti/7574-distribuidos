from common.middleware import Middleware

DISTRIBUTION_EXCHANGE = 'distribution_exchange'
FILTERED_LIKES_EXCHANGE = 'filtered_exchange'
LIKES_QUEUE = 'likes_queue'


class LikesFilterMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.exchange_declare(exchange=FILTERED_LIKES_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.queue_declare(
            queue=LIKES_QUEUE)

        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=LIKES_QUEUE)

        self.channel.basic_qos(prefetch_count=30)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(LIKES_QUEUE, lambda ch, method,
                                                properties, body: self.callback_with_ack(callback, ch, method, properties, body.decode()), False)
        self.channel.start_consuming()

    def send_video_message(self, message):
        super().send_to_exchange(FILTERED_LIKES_EXCHANGE, '', message)

    def callback_with_ack(self, callback, ch, method, properties, body):
        callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
