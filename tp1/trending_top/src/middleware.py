from common.middleware import Middleware

TRENDING_EXCHANGE = 'trending_exchange'
TRENDING_TOP_QUEUE = 'trending_top_queue'
RESULTS_QUEUE = 'results_queue'


class TrendingTopMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.queue_declare(queue=TRENDING_TOP_QUEUE)
        self.channel.queue_declare(queue=RESULTS_QUEUE)

    def recv_result_message(self, callback):

        self.vid_msg_tag = super().recv_message(TRENDING_TOP_QUEUE, lambda ch, method,
                                                properties, body: callback(body.decode()), True)
        self.channel.start_consuming()

    def send_result_message(self, message):

        super().send_message(RESULTS_QUEUE, message)
