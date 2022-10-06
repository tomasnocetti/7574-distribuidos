from common.middleware import Middleware

CATEGORIES_COUNT_EXCHANGE = 'categories_count_exchange'
CATEGORIES_EXCHANGE = 'categories_exchange'
VIDEO_DATA_QUEUE = 'video_data'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'


class JoinerMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.exchange_declare(exchange=CATEGORIES_EXCHANGE,
                                      exchange_type='fanout')
        self.channel.exchange_declare(exchange=CATEGORIES_COUNT_EXCHANGE,
                                      exchange_type='fanout')
        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE)

        self.channel.basic_qos(prefetch_count=30)

    def stop_recv_category_message(self):
        super().stop_recv_message(self.cat_msg_tag)

    def stop_recv_video_message(self):
        super().stop_recv_message(self.vid_msg_tag)

    def recv_category_message(self, callback):
        result = self.channel.queue_declare(queue='', auto_delete=True)

        self.channel.queue_bind(
            exchange=CATEGORIES_EXCHANGE, queue=result.method.queue)

        self.cat_msg_tag = super().recv_message(result.method.queue, lambda ch, method,
                                                properties, body: callback(body.decode()), True)

        self.channel.start_consuming()

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(VIDEO_DATA_QUEUE, lambda ch, method,
                                                properties, body: self.callback_with_ack(callback, ch, method, properties, body.decode()), False)
        self.channel.start_consuming()

    def send_category_count(self, message):
        super().send_to_exchange(CATEGORIES_COUNT_EXCHANGE, '', message)

    def send_video_message(self, message):
        super().send_to_exchange(DISTRIBUTION_EXCHANGE, '', message)

    def callback_with_ack(self, callback, ch, method, properties, body):
        callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
