from common.middleware import Middleware

TRENDING_EXCHANGE = 'trending_exchange'
TRENDING_TOP_QUEUE = 'trending_top_queue'


class TrendingInstanceMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=TRENDING_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(queue=TRENDING_TOP_QUEUE)

        result = self.channel.queue_declare(queue='', exclusive=True)

        self.input_queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=TRENDING_EXCHANGE, queue=self.input_queue_name, routing_key=instance_nr)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.input_queue_name, lambda ch, method,
                                                properties, body: callback(body.decode()), True)
        self.channel.start_consuming()

    def send_result_message(self, message):

        super().send_message(TRENDING_TOP_QUEUE, message)
