from common.middleware import Middleware

TRENDING_EXCHANGE = 'trending_exchange'
FILTERED_LIKES_EXCHANGE = 'filtered_exchange'


class TrendingRouterMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=FILTERED_LIKES_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.exchange_declare(exchange=TRENDING_EXCHANGE,
                                      exchange_type='direct')

        result = self.channel.queue_declare(queue='', exclusive=True)

        self.input_queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=FILTERED_LIKES_EXCHANGE, queue=self.input_queue_name)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.input_queue_name, lambda ch, method,
                                                properties, body: callback(body.decode()), True)
        self.channel.start_consuming()

    def send_video_message(self, message, id):

        super().send_to_exchange(TRENDING_EXCHANGE, id, message)
